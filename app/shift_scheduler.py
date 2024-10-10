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




def run_shift_scheduling_test():
    model = pyo.ConcreteModel()
    Day = list(range(1, 32))
    Emp = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']

    # 変数の定義
    model.x = pyo.Var(Emp, Day, within=pyo.Binary)

    # 提出されたシフト
    submitted_shift = {
        'a': [1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1],
        'b': [0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1],
        'c': [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        'd': [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
        'e': [1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1],
        'f': [0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1],
        'g': [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        'h': [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
        'i': [1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1],
        'j': [0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1]
    }


    # 目的関数の定義
    def obj_rule(model):    
        return sum((model.x[e, d] - submitted_shift[e][d-1]) ** 2 for e in Emp for d in Day)
    model.objective = pyo.Objective(rule=obj_rule, sense=pyo.minimize)


    # 出勤希望日
    def shift_constraint(model, e, d):
        if submitted_shift[e][d-1] == 0:
            return model.x[e, d] == 0
        return pyo.Constraint.Skip

    model.shift_constraint = pyo.Constraint(Emp, Day, rule=shift_constraint)

    # 出勤人数の制約
    # TODO: ルールベースでの制約を設定する
    def employee_count_constraint(model, d):
        return (3, sum(model.x[e, d] for e in Emp), 7)

    model.employee_count_constraint = pyo.Constraint(Day, rule=employee_count_constraint)


    # # 最低でも週1回は出勤する
    # def weekly_work_constraint(model, e, w):
    #     return sum(model.x[e, d] for d in range(w*7+1, min((w+1)*7+1, 32))) >= 1
    # model.weekly_work_constraint = pyo.Constraint(Emp, range(5), rule=weekly_work_constraint)

    # 求解
    opt = SolverFactory("scip", solver_io="nl")
    status = opt.solve(model)
    print('Status:', status.solver.termination_condition)

    # シフトの表示
    shift_list = []
    for e in Emp:
        shift_array = []
        for d in Day:
            if pyo.value(model.x[e, d]) > 0.8:
                shift_array.append(1)
            else:
                shift_array.append(0)
        shift_list.append({"name": e, "shift": shift_array})
        print(f"従業員 {e} のシフト:")
        for shift in shift_array:
            print(shift, end=" ")
        print()

    import json
    shift_json = json.dumps(shift_list, ensure_ascii=False)
    print(shift_json)
    return shift_list

    # # 各曜日の人数の合計を表示
    # for d in Day:
    #     total_employees = sum(pyo.value(model.x[e, d]) for e in Emp)
    #     print(f"曜日 {d} の出勤人数: {total_employees}")

    

        