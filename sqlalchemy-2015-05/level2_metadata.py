import sqlalchemy as sa
from sqlalchemy import sql

engine = sa.create_engine("postgresql://blog:blog@192.168.32.42/blog",
                          echo=True)

metadata = sa.MetaData(bind=engine)

users = sa.Table('users', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('firstname', sa.String, nullable=False),
                 sa.Column('lastname', sa.String, nullable=False),
                 sa.Column('username', sa.String, nullable=False)
                 )

posts = sa.Table('posts', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('title', sa.String, nullable=False),
                 sa.Column('article', sa.Text, nullable=False),
                 sa.Column('publication',
                           sa.DateTime,
                           default=sql.func.now(),
                           nullable=False),
                 sa.Column('author_id', sa.Integer, sa.ForeignKey('users.id'))
                 )

comments = sa.Table('comments', metadata,
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('body', sa.Text, nullable=False),
                    sa.Column('publication',
                              sa.DateTime,
                              default=sql.func.now(),
                              nullable=False),
                    sa.Column('post_id', sa.Integer, sa.ForeignKey('posts.id')),
                    sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'))
                    )


metadata.drop_all()
metadata.create_all()


def print_sql(query):
    print "==============================================="
    print "QUERY: ", str(query)
    print "ARGS: ", query.compile().params
    print "==============================================="


def insert_user(firstname, lastname, username=None):
    if not username:
        username = firstname[0] + lastname

    query = (users
             .insert()
             .values(firstname=firstname,
                     lastname=lastname,
                     username=username)
             )

    print_sql(query)

    with engine.connect() as connection:
        result = connection.execute(query)
        print "Primary key:", result.inserted_primary_key


def populate_users():
    userlist = [
        {'firstname': 'John', 'lastname': 'Doe', 'username': 'jdoe'},
        {'firstname': 'Joe', 'lastname': 'Speffer', 'username': 'jspeffer'},
        {'firstname': 'Robert', 'lastname': 'Smith', 'username': 'rsmith'},
        {'firstname': 'Wendy', 'lastname': 'Walker', 'username': 'wwalker'},
    ]

    query = users.insert()

    print_sql(query)

    with engine.connect() as connection:
        connection.execute(query, userlist)


def select_all_users():
    query = sql.select([users])

    print_sql(query)

    with engine.connect() as connection:
        result = connection.execute(query)

        for row in result:
            print row


def select_joes():
    query = (sql.select([users.c.firstname,
                         users.c.lastname])
             .where(users.c.firstname.ilike("Jo%"))
             )

    print_sql(query)

    with engine.connect() as connection:
        result = connection.execute(query)

        for row in result:
            print row


def populate_posts():
    john_id_query = (sql.select([users.c.id])
                     .where(users.c.firstname == 'John')
                     .as_scalar())

    print_sql(john_id_query)

    wendy_id_query = (sql.select([users.c.id])
                      .where(users.c.firstname == 'Wendy')
                      .as_scalar())

    print_sql(wendy_id_query)

    john_post_query = (posts.insert()
                       .values(title='First post',
                               article='F1R$T P0$T !!!',
                               author_id=john_id_query)
                       )

    print_sql(john_post_query)

    wendy_post_query = (posts.insert()
                        .values(title='Lorem',
                                article='Lorem Ipsum',
                                author_id=wendy_id_query))

    print_sql(wendy_post_query)

    with engine.connect() as connection:
        connection.execute(john_post_query)
        connection.execute(wendy_post_query)


def populate_comments():
    robert_id_query = (sql.select([users.c.id])
                       .where(users.c.firstname == 'Robert')
                       .as_scalar())

    print_sql(robert_id_query)

    first_post_id_query = (sql.select([posts.c.id])
                           .where(posts.c.title == 'First post')
                           .as_scalar())

    print_sql(first_post_id_query)

    lorem_post_id_query = (sql.select([posts.c.id])
                           .where(posts.c.title == 'Lorem')
                           .as_scalar())

    print_sql(lorem_post_id_query)

    first_comment = (comments
                     .insert()
                     .values(body='Stop reading XKCD !',
                             post_id=first_post_id_query,
                             user_id=robert_id_query)
                     )

    print_sql(first_comment)

    second_comment = (comments
                      .insert()
                      .values(body='Do u speak latin ?',
                              post_id=lorem_post_id_query,
                              user_id=robert_id_query)
                      )

    print_sql(second_comment)

    with engine.connect() as connection:
        connection.execute(first_comment)
        connection.execute(second_comment)


def view_comments():
    authors = users.alias('authors')
    commenters = users.alias('commenters')

    query = (
        sql.select([
            posts.c.title.label('post_title'),
            (authors.c.firstname + authors.c.lastname).label('author_fullname'),
            comments.c.publication.label('published_at'),
            (commenters.c.firstname + commenters.c.lastname).label('commenter_fullname'),
            comments.c.body.label('comment')
        ])
        .select_from(
            posts.join(authors,
                       posts.c.author_id == authors.c.id)
            .join(comments,
                  comments.c.post_id == posts.c.id)
            .join(commenters,
                  commenters.c.id == comments.c.user_id)
        )
        .where(commenters.c.username == 'rsmith')
    )

    print_sql(query)

    with engine.connect() as connection:
        result = connection.execute(query)
        for row in result:
            print row


def update_post():
    query = (posts
             .update()
             .where(posts.c.title == 'First post')
             .values(article='F1R$T P0$T ROFLMAOMGZZZ 1!!1 ONE !')
             )

    print_sql(query)

    with engine.connect() as connection:
        connection.execute(query)



if __name__ == "__main__":
    insert_user('Lord', 'Sanderson')
    #populate_users()
    #select_all_users()
    #select_joes()
    #populate_posts()
    #populate_comments()
    #view_comments()
    #update_post()
