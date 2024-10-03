from sqlalchemy.orm import Session
from app.models import User, Availability, Schedule, DailyConstraint
from app.schemas.schemas import ScheduleCreate
from app.crud.schedule import crud_schedule
from datetime import date
import pyomo.environ as pyo
from pyomo.opt import SolverFactory

def run_shift_scheduling(db: Session):
    # データの取得
    users = db.query(User).all()
    availabilities = db.query(Availability).all()
    daily_constraints = db.query(DailyConstraint).all()

    # ユーザーと日付のリスト
    Users = [u.id for u in users]
    Dates = [dc.date for dc in daily_constraints]

    # シフト希望の辞書作成
    availability_dict = {}
    for av in availabilities:
        availability_dict[(av.user_id, av.date)] = av.is_available

    # デイリー制約の辞書作成
    daily_constraints_dict = {dc.date: dc for dc in daily_constraints}

    # モデルの定義
    model = pyo.ConcreteModel()

    # 変数の定義
    model.x = pyo.Var(Users, Dates, within=pyo.Binary)

    # 目的関数：シフト希望との乖離を最小化
    def obj_rule(model):
        return sum((model.x[u, d] - availability_dict.get((u, d), 0)) ** 2 for u in Users for d in Dates)
    model.objective = pyo.Objective(rule=obj_rule, sense=pyo.minimize)

    # シフト希望を考慮した制約
    def availability_constraint(model, u, d):
        if not availability_dict.get((u, d), False):
            return model.x[u, d] == 0
        else:
            return pyo.Constraint.Skip
    model.availability_constraint = pyo.Constraint(Users, Dates, rule=availability_constraint)

    # 日付ごとの従業員数の制約
    def employee_count_constraint(model, d):
        dc = daily_constraints_dict.get(d)
        return (dc.min_employees, sum(model.x[u, d] for u in Users), dc.max_employees)
    model.employee_count_constraint = pyo.Constraint(Dates, rule=employee_count_constraint)

    # 求解
    solver = SolverFactory('glpk')  # または他の適切なソルバー
    result = solver.solve(model)

    # 結果の保存
    for u in Users:
        for d in Dates:
            assigned = pyo.value(model.x[u, d]) > 0.5
            schedule_in = ScheduleCreate(
                user_id=u,
                date=d,
                assigned=assigned
            )
            crud_schedule.create(db, obj_in=schedule_in)
