from flask import Blueprint, render_template, Response, jsonify
from app.sse import event_stream
from app.redis import redis_client
from app.models import Option, Poll

screen_bp = Blueprint("screen", __name__)


@screen_bp.route("/screen")
def screen():
    poll_id = redis_client.get("active_poll")

    # if not poll_id:
    #     return render_template("screen_empty.html")

    poll = Poll.query.get(poll_id)
    options = Option.query.filter_by(poll_id=poll_id).all()

    return render_template(
        "screen.html",
        poll=poll,
        options=options
    )


@screen_bp.route("/screen/stream")
def stream():
    poll_id = redis_client.get("active_poll")
    if not poll_id:
        return "", 204

    return Response(
        event_stream(poll_id),
        mimetype="text/event-stream"
    )


@screen_bp.route("/screen/stats")
def poll_stats():
    poll_id = redis_client.get("active_poll")
    if not poll_id:
        return jsonify([])

    options = Option.query.filter_by(poll_id=poll_id).all()

    data = []
    for opt in options:
        count = redis_client.get(f"poll:{poll_id}:option:{opt.id}")
        data.append({
            "label": opt.text,
            "count": int(count or 0)
        })

    return jsonify(data)


@screen_bp.route("/screen/state")
def screen_state():
    poll_id = redis_client.get("active_poll")

    if not poll_id:
        return jsonify({
            "active": False
        })

    poll = Poll.query.get(poll_id)

    return jsonify({
        "active": True,
        "poll_id": poll.id,
        "question": poll.question
    })


@screen_bp.route("/screen/chat")
def chat_history():
    poll_id = redis_client.get("active_poll")
    if not poll_id:
        return jsonify([])

    messages = redis_client.lrange(f"chat:approved:{poll_id}", 0, -1)

    return jsonify(messages)

