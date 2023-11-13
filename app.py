# postirony!
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, desc


class Base(DeclarativeBase):
    pass


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Post(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    pretext: Mapped[str] = mapped_column(String, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)
    edit_key: Mapped[str] = mapped_column(String)

    def __repr__(self):
        return self.title


class Comments(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    pid: Mapped[int] = mapped_column(Integer, nullable=False)
    key: Mapped[str] = mapped_column(String)

    def __repr__(self):
        return self.name


with app.app_context():
    db.create_all()


@app.route('/')
def index():
    posts = Post.query.order_by(desc(Post.id)).all()
    return render_template('index.html', data=posts)


@app.route('/author/<string:name>')
def author(name):
    names = Post.query.order_by(desc(Post.id)).all()
    return render_template('authors-post.html', data=names, name=name)


@app.route('/search', methods=["POST", "GET"])
def search():
    if request.method == "POST":
        name = request.form["author"]
        searching = Post.query.order_by(desc(Post.id)).all()
        return render_template('authors-post.html', data=searching, name=name)
    else:
        return render_template('search.html')


@app.route('/pname', methods=['POST', 'GET'])
def pname():
    if request.method == 'POST':
        post = request.form["title"]
        searching = Post.query.order_by(desc(Post.id)).all()
        return render_template('pname.html', data=searching, name=post)
    else:
        return render_template('sname.html')


@app.route('/posts/<int:id>/comment', methods=['POST', 'GET'])
def comment(id):
    if request.method == 'POST':
        name = request.form['name']
        pid = request.form['pid']
        text = request.form['text']
        key = request.form['key']
        comment = Comments(name=name, pid=pid, text=text, key=key)
        try:
            db.session.add(comment)
            db.session.commit()
            return redirect(f'/posts/{id}')
        except:
            return render_template('error.html')
    else:
        post = db.session.get(Post, id)
        return render_template('comment.html', post=post)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/posts/<int:id>', methods=['POST', 'GET'])
def posts(id):
    post = db.session.get(Post, id)
    comment = Comments.query.order_by(desc(Comments.id)).all()
    return render_template('posts.html', post=post, comment=comment)


@app.route('/posts/<int:id>/auth-editor', methods=['POST', 'GET'])
def auth_editor(id):
    if request.method == 'POST':
        key = request.form['edit_key']
        return redirect(f'/posts/{id}/{key}/edit')
    else:
        return render_template('auth-editor.html')


@app.route('/posts/<int:id>/<string:key>/del')
def posts_delete(id, key):
    post_delete = Post.query.get_or_404(id)
    if post_delete.edit_key == key:
        try:
            db.session.delete(post_delete)
            db.session.commit()
            return render_template('successfully-del.html')
        except:
            return render_template('error.html')
    else:
        return render_template('error-key.html')


@app.route('/comments/<int:id>/cedit', methods=['POST', 'GET'])
def auth_com(id):
    if request.method == 'POST':
        key = request.form['key']
        return redirect(f'/comments/{id}/{key}/cedit')
    else:
        return render_template('auth-com.html')


@app.route('/comments/<int:id>/<string:key>/cedit', methods=['POST', 'GET'])
def comments(id, key):
    comment = Comments.query.get_or_404(id)
    if comment.key == key:
        if request.method == 'POST':
            comment.name = request.form['name']
            comment.key = request.form['key']
            comment.text = request.form['text']
            try:
                db.session.commit()
                return redirect(f'/posts/{comment.pid}')
            except:
                return render_template('error.html')
        else:
            post = db.session.get(Post, comment.pid)
            return render_template('comment-edit.html', post=post, com=comment)
    else:
        return render_template('error-key.html')


@app.route('/comments/<int:id>/<string:key>/del', methods=['POST', 'GET'])
def del_comments(id, key):
    comment_delete = Comments.query.get_or_404(id)
    if comment_delete.key == key:
        try:
            pid = comment_delete.pid
            db.session.delete(comment_delete)
            db.session.commit()
            return redirect(f'/posts/{pid}')
        except:
            return render_template('error.html')
    else:
        return render_template('error-key.html')


@app.route('/posts/<int:id>/<string:key>/edit', methods=["POST", "GET"])
def post_editor(id, key):
    post_edit = Post.query.get(id)
    if post_edit.edit_key == key:
        if request.method == "POST":
            post_edit.title = request.form['title']
            post_edit.pretext = request.form['pretext']
            post_edit.author = request.form['author']
            post_edit.text = request.form['text']
            try:
                db.session.commit()
                return render_template('successfully-edit.html', post=post_edit)
            except:
                return render_template('error.html')
        else:
            return render_template('editor.html', post_edit=post_edit)
    else:
        return render_template('error-key.html')


@app.route('/create', methods=["POST", "GET"])
def create():
    if request.method == "POST":
        title = request.form['title']
        pretext = request.form['pretext']
        author = request.form['author']
        edit_key = request.form['edit_key']
        text = request.form['text']

        post_create = Post(title=title, pretext=pretext, author=author, edit_key=edit_key, text=text)
        try:
            db.session.add(post_create)
            db.session.commit()
            return render_template('successfully-create.html', post=post_create)
        except:
            return render_template('error.html')

    else:
        return render_template('create.html')


if __name__ == "__main__":
    app.run(debug=False)
