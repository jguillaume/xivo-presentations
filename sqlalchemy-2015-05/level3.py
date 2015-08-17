import sqlalchemy as sa
from sqlalchemy import sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, aliased

engine = sa.create_engine("postgresql://blog:blog@192.168.32.42/blog",
                          echo=True)

Base = declarative_base()


class User(Base):

    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True)
    firstname = sa.Column(sa.String, nullable=False)
    lastname = sa.Column(sa.String, nullable=False)
    username = sa.Column(sa.String, nullable=False)


class Post(Base):

    __tablename__ = 'posts'

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String, nullable=False)
    article = sa.Column(sa.Text, nullable=False)
    publication = sa.Column(sa.DateTime,
                            default=sql.func.now(),
                            nullable=False)

    author_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))

    author = relationship("User")


class Comment(Base):

    __tablename__ = 'comments'

    id = sa.Column(sa.Integer, primary_key=True)
    body = sa.Column(sa.Text, nullable=False)
    publication = sa.Column(sa.DateTime,
                            default=sql.func.now(),
                            nullable=False)

    post_id = sa.Column(sa.Integer, sa.ForeignKey('posts.id'))
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))

    post = relationship("Post")
    user = relationship("User")


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


def print_sql(query):
    print "==============================================="
    print "QUERY: ", str(query)
    print "==============================================="


def insert_user(firstname, lastname, username=None):
    if not username:
        username = firstname[0] + lastname

    user = User(firstname=firstname,
                lastname=lastname,
                username=username)

    session = Session()
    session.add(user)
    session.commit()

    print "User id:", user.id


def populate_users():
    userlist = [
        User(firstname='John', lastname='Doe', username='jdoe'),
        User(firstname='Joe', lastname='Speffer', username='jspeffer'),
        User(firstname='Robert', lastname='Smith', username='rsmith'),
        User(firstname='Wendy', lastname='Walker', username='wwalker'),
    ]

    session = Session()
    session.add_all(userlist)
    session.commit()


def select_all_users():
    session = Session()
    query = session.query(User)

    print_sql(query)

    for user in query.all():
        print user.firstname, user


def select_joes():
    session = Session()
    query = (session.query(User.firstname,
                           User.lastname)
             .filter(User.firstname.ilike("Jo%"))
             )

    print_sql(query)

    for row in query.all():
        print row


def populate_posts():
    session = Session()

    john_query = session.query(User).filter(User.firstname == 'John')
    wendy_query = session.query(User).filter(User.firstname == 'Wendy')

    print_sql(john_query)
    print_sql(wendy_query)

    john = john_query.first()
    wendy = wendy_query.first()

    john_post = Post(title='First post',
                     article='F1R$T P0$T !!!',
                     author=john)

    wendy_post = Post(title='Lorem',
                      article='Lorem Ipsum',
                      author=wendy)

    session.add(john_post)
    session.add(wendy_post)
    session.commit()


def populate_comments():
    session = Session()

    robert_query = session.query(User).filter(User.firstname == 'Robert')
    first_post_query = session.query(Post).filter(Post.title == 'First post')
    lorem_post_query = session.query(Post).filter(Post.title == 'Lorem')

    print_sql(robert_query)
    print_sql(first_post_query)
    print_sql(lorem_post_query)

    robert = robert_query.first()
    first_post = first_post_query.first()
    lorem_post = lorem_post_query.first()

    first_comment = Comment(body='Stop Reading XKCD !',
                            user=robert,
                            post=first_post)

    second_comment = Comment(body='Do u speak latin ?',
                             user=robert,
                             post=lorem_post)

    session.add(first_comment)
    session.add(second_comment)
    session.commit()


def view_comments():
    session = Session()

    Author = aliased(User)
    Commenter = aliased(User)

    query = (
        session.query(
            Post.title.label('post_title'),
            (Author.firstname + Author.lastname).label('author_fullname'),
            (Commenter.firstname + Commenter.lastname).label('commenter_fullname'),
            Comment.publication.label('published_at'),
            Comment.body.label('comment')
        )
        .join(Post, Comment.post)
        .join(Author, Post.author)
        .join(Commenter, Comment.user)
        .filter(Commenter.username == 'rsmith')
    )

    print_sql(query)

    for row in query.all():
        print (row.post_title,
               row.author_fullname,
               row.commenter_fullname,
               row.published_at,
               row.comment)


if __name__ == "__main__":
    insert_user('Lord', 'Sanderson')
    populate_users()
    select_all_users()
    select_joes()
    populate_posts()
    populate_comments()
    view_comments()
