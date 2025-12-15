from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.db import db
from app.models import Poll, Option, Answer
from app.redis import redis_client

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/poll/create", methods=["GET", "POST"])
def create_poll():
    if request.method == "POST":
        question = request.form.get("question")
        allow_text = bool(request.form.get("allow_text"))

        options = request.form.getlist("options[]")
        options = [o.strip() for o in options if o.strip()]

        if not question or len(options) < 2:
            return "Нужно минимум 2 варианта ответа", 400

        poll = Poll(
            question=question,
            allow_text=allow_text
        )
        db.session.add(poll)
        db.session.flush()  # получаем poll.id

        for text in options:
            db.session.add(
                Option(poll_id=poll.id, text=text)
            )

        db.session.commit()

        return redirect(url_for("admin.poll_created", poll_id=poll.id))

    return render_template("admin/create_poll.html")


@admin_bp.route("/poll/created/<int:poll_id>")
def poll_created(poll_id):
    return render_template("admin/poll_created.html", poll_id=poll_id)


@admin_bp.route("/poll/<int:poll_id>/activate", methods=["POST"])
def activate_poll(poll_id):
    redis_client.set("active_poll", poll_id)
    return redirect("/admin/polls")


@admin_bp.route("/poll/deactivate", methods=["POST"])
def deactivate_poll():
    poll_id = redis_client.get("active_poll")

    # if poll_id:
    #     redis_client.delete(
    #         f"chat:pending:{poll_id}",
    #         f"chat:approved:{poll_id}"
    #     )

    redis_client.delete("active_poll")
    return redirect("/admin/polls")


@admin_bp.route("/polls")
def polls_list():
    polls = Poll.query.order_by(Poll.id.desc()).all()
    active_poll_id = redis_client.get("active_poll")

    return render_template(
        "admin/polls_list.html",
        polls=polls,
        active_poll_id=int(active_poll_id) if active_poll_id else None
    )


@admin_bp.route("/moderation")
def moderation_page():
    return render_template("admin/moderation.html")


@admin_bp.route("/moderation/pending")
def moderation_pending():
    poll_id = redis_client.get("active_poll")
    if not poll_id:
        return jsonify([])

    return jsonify(
        redis_client.lrange(f"chat:pending:{poll_id}", 0, -1)
    )


@admin_bp.route("/moderation/state")
def moderation_state():
    poll_id = redis_client.get("active_poll")
    return jsonify({
        "active": bool(poll_id),
        "poll_id": int(poll_id) if poll_id else None
    })


@admin_bp.route("/moderation/approve", methods=["POST"])
def moderation_approve():
    poll_id = redis_client.get("active_poll")
    text = request.json["text"]

    redis_client.lrem(f"chat:pending:{poll_id}", 1, text)
    redis_client.rpush(f"chat:approved:{poll_id}", text)
    redis_client.publish(f"chat:{poll_id}", text)

    return jsonify({"ok": True})


@admin_bp.route("/moderation/reject", methods=["POST"])
def moderation_reject():
    poll_id = redis_client.get("active_poll")
    text = request.json["text"]

    redis_client.lrem(f"chat:pending:{poll_id}", 1, text)
    return jsonify({"ok": True})


@admin_bp.route("/poll/<int:poll_id>/clear", methods=["POST"])
def clear_poll_answers(poll_id):
    # 1. PostgreSQL — удаляем ответы
    Answer.query.filter_by(poll_id=poll_id).delete()
    db.session.commit()

    # 2. Redis — статистика по вариантам
    keys = redis_client.keys(f"poll:{poll_id}:option:*")
    if keys:
        redis_client.delete(*keys)

    # 3. Redis — чат (модерация + показ)
    redis_client.delete(
        f"chat:pending:{poll_id}",
        f"chat:approved:{poll_id}"
    )

    # 4. Redis — защита от повторных ответов
    answered_keys = redis_client.keys(f"answered:{poll_id}:*")
    if answered_keys:
        redis_client.delete(*answered_keys)

    return redirect("/admin/polls")


