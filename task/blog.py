from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from task.auth import login_required
from task.db import get_db

bp = Blueprint("blog", __name__)

@bp.route("/",methods=("GET","POST"))
def index():
    db = get_db()
    if request.method == "POST":
        search = request.form["search"]
        error = None

        if not search:
            error = "Title is required."
    
        if error is not None:
            flash(error)
        posts = db.execute(
                "SELECT p.id, title, body, tag, created, author_id, username"
                " FROM post p JOIN user u ON p.author_id = u.id"
                " WHERE p.title LIKE ?",
                ('%'+search+'%',),
            ).fetchall()
        if not posts:
            posts = db.execute(
                "SELECT p.id, title, body, tag, created, author_id, username"
                " FROM post p JOIN user u ON p.author_id = u.id"
                " WHERE p.tag LIKE ?",
                ('%'+search+'%',),
            ).fetchall()
    else:
        posts = db.execute(
            "SELECT p.id, title, body, tag, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " ORDER BY created DESC"
        ).fetchall()

    ans = db.execute(
        "SELECT a.id, comment, time_added, post_id, author_c"
        " FROM answer a JOIN post p ON a.post_id = p.id"
        " ORDER BY created DESC"
    ).fetchall()

    return render_template("blog/index.html",  **locals())


def get_post(id, check_author=True):

    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, tag, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


def get_ans(id):
    
    ans = (
        get_db()
        .execute(
            "SELECT a.id, comment, post_id, author_c"
            " FROM answer a JOIN post p ON a.post_id = p.id"
            " WHERE a.id = ?",
            (id,),
        )
        .fetchone()
    )

    if ans is None:
        abort(404, "Answer id {0} doesn't exist.".format(id))

    return ans


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        tag = request.form["tag"]
        error = None

        if not title:
            error = "Title is required."
        if not body:
            error = "Description is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, tag, author_id) VALUES (?, ?, ?, ?)",
                (title, body, tag, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        tag = request.form["tag"]
        error = None

        if not title:
            error = "Title is required."
        if not body:
            error = "Description is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ?, tag = ? WHERE id = ?", (title, body, tag, id)
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))


@bp.route("/<int:id>/answer", methods=("GET","POST"))
@login_required
def answer(id):
    post = (
        get_db()
        .execute(
            "SELECT id, body FROM post" 
            " WHERE id = ?",
            (id,),
        )
        .fetchone()
    )
    if request.method == "POST":
        comment = request.form["ans"]
        error = None

        if not comment:
            error = "Answer is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO answer (comment, post_id, author_c) VALUES (?, ?, ?)",
                (comment, id, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("blog.index"))
        
    return render_template("blog/answer.html",post=post)


@bp.route("/<int:id>/update_ans", methods=("GET", "POST"))
@login_required
def update_ans(id):
    answer = get_ans(id)
    if request.method == "POST":
        comment = request.form["ans"]
        error = None

        if not comment:
            error = "Answer is required."
    
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE answer SET comment = ? WHERE id = ?", (comment, id)
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update_ans.html", answer=answer)


@bp.route("/<int:id>/delete_ans", methods=("POST",))
@login_required
def delete_ans(id):
    get_ans(id)
    db = get_db()
    db.execute("DELETE FROM answer WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))