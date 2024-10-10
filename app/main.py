from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models
from app.schemas.schemas import UserCreate, User, UserUpdate, AvailabilityCreate, Availability, AvailabilityUpdate, ScheduleCreate, Schedule, ScheduleUpdate, DailyConstraintCreate, DailyConstraintUpdate, DailyConstraint, Token, WeekdayDefaults, HolidayDefaults
from app.crud.user import crud_user 
from app.crud.availability import crud_availability
from app.crud.schedule import crud_schedule
from app.crud.daily_constraint import crud_daily_constraint
from app.database import engine, get_db
from app.auth import authenticate_user, create_access_token, get_current_user, get_password_hash
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from datetime import date, datetime, timedelta
from app.shift_scheduler import run_shift_scheduling, run_shift_scheduling_test
from sqladmin import Admin, ModelView

app = FastAPI()

# TODO: https://qiita.com/baby-degu/items/6f516189445d98ddbb7d

async def on_startup():
    models.Base.metadata.create_all(bind=engine)


admin = Admin(app, engine=engine)

class UserAdmin(ModelView, model=models.User):
    column_list = [models.User.id]

class AvailabilityAdmin(ModelView, model=models.Availability):
    column_list = [models.Availability.id, models.Availability.user_id, models.Availability.date, models.Availability.is_available]

class ScheduleAdmin(ModelView, model=models.Schedule):
    column_list = [models.Schedule.id, models.Schedule.date, models.Schedule.user_id, models.Schedule.assigned]

class DailyConstraintAdmin(ModelView, model=models.DailyConstraint):
    column_list = [models.DailyConstraint.id, models.DailyConstraint.date, models.DailyConstraint.min_employees, models.DailyConstraint.max_employees, models.DailyConstraint.is_holiday]

admin.add_view(UserAdmin)
admin.add_view(AvailabilityAdmin)
admin.add_view(ScheduleAdmin)
admin.add_view(DailyConstraintAdmin)

# 1. 認証API

## ログイン
@app.post("/api/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    res = {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "role": user.role,
        "name": user.name
    }

    return res

## ログインユーザー情報取得
@app.get("/api/users/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

## ログインユーザー情報修正
@app.patch("/api/users/me", response_model=User)
def update_user_me(user_in: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_user = crud_user.get(db=db, id=current_user.id)
    if not db_user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません。")
    return crud_user.update(db=db, db_obj=db_user, obj_in=user_in)

# 2. ユーザー管理API

## ユーザーリスト取得
@app.get("/api/users", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="アクセスが拒否されました。")
    return crud_user.get_multi(db, skip=skip, limit=limit)

## 新規ユーザー追加
@app.post("/api/users", response_model=User)
def create_user(user_in: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="アクセスが拒否されました。")
    db_user = crud_user.get_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(status_code=400, detail="メールアドレスは既に登録されています。")
    return crud_user.create(db=db, obj_in=user_in)

# 3. シフト希望API

## シフト希望提出
@app.post("/api/availabilities", response_model=Availability)
def create_availability(availability_in: AvailabilityCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    availability_in.user_id = current_user.id
    return crud_availability.create(db=db, obj_in=availability_in)

## ユーザーのシフト希望取得
@app.get("/api/availabilities/{userId}", response_model=List[Availability])
def read_availabilities(userId: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id != userId and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="アクセスが拒否されました。")
    return crud_availability.get_by_user_id(db, user_id=userId)

## 一月の全員分のシフト取得
@app.get("/api/availabilities")
def read_monthly_availabilities(month: int, year: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="アクセスが拒否されました。")
    return crud_availability.get_monthly(db, month, year)




# 4. シフトスケジュールAPI

## シフトスケジューラ実行
@app.post("/api/schedules/run")
def run_scheduler(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="アクセスが拒否されました。")
    # 既存のスケジュールを削除
    crud_schedule.remove_all(db)
    # シフトスケジューリングを実行
    run_shift_scheduling(db)
    return {"message": "シフトスケジューリングが完了しました。"}


@app.post("/api/schedules/run-test")
def run_scheduler_test():
    # 既存のスケジュールを削除
    # シフトスケジューリングを実行
    return run_shift_scheduling_test()


# 5. デイリー制約API

## デイリー制約の取得
@app.get("/api/daily-constraints", response_model=List[DailyConstraint])
def read_daily_constraints(skip: int = 0, limit: int = 31, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="アクセスが拒否されました。")
    return crud_daily_constraint.get_multi(db, skip=skip, limit=limit)

## 特定の日付のデイリー制約を取得
@app.get("/api/daily-constraints/{date}", response_model=DailyConstraint)
def read_daily_constraint(date: date, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="アクセスが拒否されました。")
    return crud_daily_constraint.get_by_date(db, date=date)

## デイリー制約の作成
@app.post("/api/daily-constraints", response_model=DailyConstraint)
def create_daily_constraint(constraint_in: DailyConstraintCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="アクセスが拒否されました。")
    return crud_daily_constraint.create(db=db, obj_in=constraint_in)

## デイリー制約の更新
@app.patch("/api/daily-constraints/{id}", response_model=DailyConstraint)
def update_daily_constraint(id: str, constraint_in: DailyConstraintUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="アクセスが拒否されました。")
    constraint = crud_daily_constraint.get(db=db, id=id)
    if not constraint:
        raise HTTPException(status_code=404, detail="制約が見つかりません。")
    return crud_daily_constraint.update(db=db, db_obj=constraint, obj_in=constraint_in)

## デイリー制約の削除
@app.delete("/api/daily-constraints/{id}")
def delete_daily_constraint(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="アクセスが拒否されました。")
    constraint = crud_daily_constraint.get(db=db, id=id)
    if not constraint:
        raise HTTPException(status_code=404, detail="制約が見つかりません。")
    crud_daily_constraint.remove(db=db, id=id)
    return {"message": "制約が削除されました。"}


@app.post("/weekday-defaults/")
def set_weekday_defaults(defaults: WeekdayDefaults):
    if defaults.weekday < 0 or defaults.weekday > 6:
        raise HTTPException(status_code=400, detail="Invalid weekday")
    DailyConstraint.set_defaults_for_weekday(defaults.weekday, defaults.min_employees, defaults.max_employees)
    return {"message": "Weekday defaults set successfully"}

@app.post("/holiday-defaults/")
def set_holiday_defaults(defaults: HolidayDefaults):
    DailyConstraint.set_defaults_for_holiday(defaults.min_employees, defaults.max_employees)
    return {"message": "Holiday defaults set successfully"}


# 6. モニタリングAPI

## ヘルスチェック
@app.get("/health")
def health_check():
    print("health check")
    return {"status": "ok"}

## バージョン情報
@app.get("/version")
def get_version():
    return {"version": "1.0.0"}

## メトリクス
@app.get("/metrics")
def get_metrics():
    # メトリクス情報を返す（例: 平均応答時間など）
    return {"metrics": "メトリクス情報"}