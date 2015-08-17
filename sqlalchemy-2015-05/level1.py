import sqlalchemy as sa
from sqlalchemy import sql

engine = sa.create_engine("postgresql://blog:blog@192.168.32.42/blog",
                          echo=True)

connection = engine.connect()


def setup():
    query = """
    CREATE TABLE IF NOT EXISTS
    users (
        id          INT     PRIMARY KEY,
        firstname   VARCHAR NOT NULL,
        lastname    VARCHAR NOT NULL,
        username    VARCHAR NOT NULL
    )
    """

    connection.execute(query)

    query = """
    CREATE TABLE IF NOT EXISTS
    posts (
        id          INT         PRIMARY KEY,
        title       VARCHAR     NOT NULL,
        article     TEXT        NOT NULL,
        publication TIMESTAMP   NOT NULL,
        author_id   INT         FOREIGN KEY REFERENCES users.id
    )
    """

    connection.execute(query)

    query = """
    CREATE TABLE IF NOT EXISTS
    comments (
        id              INT         PRIMARY KEY,
        body            TEXT        NOT NULL,
        publication     TIMESTAMP   NOT NULL,
        post_id         INT         FOREIGN KEY REFERENCES posts.id,
        user_id         INT         FOREIGN KEY REFERENCES users.id
    )
    """

    connection.execute(query)


def cleanup():
    connection.execute("DELETE FROM comments")
    connection.execute("DELETE FROM posts")
    connection.execute("DELETE FROM users")


def insert_user(firstname, lastname, username=None):
    if not username:
        username = firstname[0] + lastname

    query = sql.text("""
    INSERT INTO users
    (
        firstname,
        lastname,
        username
    )
    VALUES
    (
        :firstname,
        :lastname,
        :username
    )
    """)

    connection.execute(query,
                       firstname=firstname,
                       lastname=lastname,
                       username=username)


def populate_users():
    userlist = [
        {'firstname': 'John', 'lastname': 'Doe', 'username': 'jdoe'},
        {'firstname': 'Joe', 'lastname': 'Speffer', 'username': 'jspeffer'},
        {'firstname': 'Robert', 'lastname': 'Smith', 'username': 'rsmith'},
        {'firstname': 'Wendy', 'lastname': 'Walker', 'username': 'wwalker'},
    ]

    for user in userlist:
        insert_user(user['firstname'], user['lastname'], user['username'])


def select_all_users():
    query = """
    SELECT
        *
    FROM
        users
    """

    result = connection.execute(query)
    for row in result:
        print row


def select_joes():
    query = sql.text("""
    SELECT
        firstname,
        lastname
    FROM
        users
    WHERE
        firstname ILIKE :firstname_like
    """)

    result = connection.execute(query, firstname_like='Jo%')

    for row in result:
        print row[0], row[1]


def populate_posts():
    query = sql.text("""
    INSERT INTO posts
    (
        title,
        article,
        author_id,
        publication
    )
    VALUES
    (
        :title,
        :article,
        (SELECT id FROM users WHERE firstname = :firstname),
        now()
    )
    """)

    connection.execute(query,
                       title='First post',
                       article='F1R$T P0$T !!!',
                       firstname='John')

    connection.execute(query,
                       title='Lorem',
                       article='Lorem Ipsum',
                       firstname='Wendy')


def populate_comments():
    query = sql.text("""
    INSERT INTO comments
    (
        body,
        post_id,
        user_id,
        publication
    )
    VALUES
    (
        :body,
        (SELECT id FROM posts WHERE title = :post_title),
        (SELECT id FROM users WHERE firstname = :author_firstname),
        now()
    )
    """)

    connection.execute(query,
                       body='Stop reading XKCD !',
                       post_title='First post',
                       author_firstname='Robert')

    connection.execute(query,
                       body='Do u speak latin ?',
                       post_title='Lorem',
                       author_firstname='Robert')


def view_comments():
    query = """
    SELECT
        posts.title                                         AS post_title,
        authors.firstname || ' ' || authors.lastname        AS author_fullname,
        commenters.firstname || ' ' || commenters.lastname  AS commenter_fullname,
        comments.body                                       AS comment
    FROM
        posts
        INNER JOIN users AS authors
            ON posts.author_id = authors.id
        INNER JOIN comments
            ON comments.post_id = posts.id
            INNER JOIN users AS commenters
                ON comments.user_id = commenters.id
    WHERE
        commenters.username = 'rsmith'
    """

    result = connection.execute(query)
    for row in result:
        line = " | ".join([row['post_title'],
                           row['author_fullname'],
                           row['commenter_fullname'],
                           row['comment']])
        print line


def update_post():
    query = sql.text("""
    UPDATE
        posts
    SET
        article = :article
    WHERE
        title = :title
    """)

    connection.execute(query,
                       article='F1R$T P0$T ROFLMAOMGZZZ 1!!1 ONE !',
                       title='First post')


def delete_post():
    query = sql.text("""
    DELETE FROM
        comments
    WHERE
        comments.post_id = (SELECT id FROM posts WHERE title = :title)
    """)

    connection.execute(query, title='First post')

    query = sql.text("""
    DELETE FROM
        posts
    WHERE
        posts.title = :title
    """)

    connection.execute(query, title='First post')


def test_scalar():
    query = """
    SELECT
        id
    FROM
        users
    """

    result = connection.execute(query)
    print result.scalar()


if __name__ == "__main__":
    cleanup()
    test_scalar()
    #insert_user('Lord', 'Sanderson')
    #populate_users()
    #select_all_users()
    #select_joes()
    #populate_posts()
    #populate_comments()
    #view_comments()
    #update_post()
    #delete_post()
