import uuid
from flask import Blueprint, render_template, request, jsonify
from app.models import Poll, Option, Answer
from app.db import db
from app.redis import redis_client

poll_bp = Blueprint("poll", __name__)


@poll_bp.route("/poll")
def poll_page():
    user_id = str(uuid.uuid4())
    return render_template("poll.html", user_id=user_id)


@poll_bp.route("/poll/state")
def poll_state():
    poll_id = redis_client.get("active_poll")

    if not poll_id:
        return jsonify({
            "active": False
        })

    poll = Poll.query.get(poll_id)
    options = Option.query.filter_by(poll_id=poll_id).all()

    return jsonify({
        "active": True,
        "poll_id": poll.id,
        "question": poll.question,
        "allow_text": poll.allow_text,
        "options": [
            {"id": o.id, "text": o.text}
            for o in options
        ]
    })


@poll_bp.route("/poll/answer", methods=["POST"])
def submit_answer():
    data = request.json
    user_id = data["user_id"]

    poll_id = redis_client.get("active_poll")
    if not poll_id:
        return jsonify({"error": "no active poll"}), 400

    redis_key = f"answered:{poll_id}:{user_id}"

    if not redis_client.setnx(redis_key, 1):
        return jsonify({"error": "already answered"}), 400

    redis_client.expire(redis_key, 3600)

    answer = Answer(
        poll_id=poll_id,
        user_id=user_id,
        option_id=data.get("option_id"),
        text_answer=data.get("text")
    )

    db.session.add(answer)
    db.session.commit()

    if data.get("option_id"):
        redis_client.incr(f"poll:{poll_id}:option:{data['option_id']}")

    if data.get("text"):
        redis_client.rpush(
            f"chat:pending:{poll_id}",
            data["text"]
        )

    return jsonify({"ok": True})

