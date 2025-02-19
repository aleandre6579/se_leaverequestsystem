from datetime import datetime

from flask import redirect, request, session

from ..db import leave
from ..db.models import LeaveRequest
from ..extensions import db


def delete_leave(leave_id: int):
    leave_to_delete = LeaveRequest.query.filter_by(id=leave_id).first()
    if leave_to_delete is None:
        return f"Leave with id {leave_id} does not exist", 404

    # Check if the logged-in user is the owner of the request
    if leave_to_delete.user_id == session.get("user_id"):
        if leave.start_date_passed(leave_to_delete.date_start):
            return "Cannot delete because the start date has already passed", 400

        try:
            db.session.delete(leave_to_delete)
            db.session.commit()
            return {"delete_success": True}
        except Exception as e:
            print(f"Error: {e}")
            return "There was an issue deleting your task", 500
    else:
        return "You do not have permission to delete this request", 403


def post_leave():
    user_id = session.get("user_id")
    leave_reason = request.form["reason"]
    leave_date_start_str = request.form["date_start"]
    leave_date_end_str = request.form["date_end"]

    try:
        leave_date_start = datetime.strptime(leave_date_start_str, "%Y-%m-%d")
        leave_date_end = datetime.strptime(leave_date_end_str, "%Y-%m-%d")
    except ValueError:
        return "Please enter valid dates", 400

    if not leave.validates_same_day_conflict(leave_date_start):
        return "Can't have 2 leaves starting on the same day", 400

    quota = 10
    if not leave.validates_leave_quota(leave_date_start, quota):
        return f"You cannot have more than {quota} leaves in a year!", 400

    max_days = 60
    if not leave.validates_max_leave_date(leave_date_start, max_days):
        return f"You cannot request leave over {max_days} days from now!", 400

    new_leave = LeaveRequest(
        reason=leave_reason,
        date_start=leave_date_start,
        date_end=leave_date_end,
        user_id=user_id,
    )

    try:
        db.session.add(new_leave)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        print(f"Error: {e}")
        return "There was an issue adding your task", 500
