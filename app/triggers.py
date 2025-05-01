from sqlalchemy import event, DDL

from app.models.models import Thread


update_post_thread_count_func = DDL(
    """\
    CREATE OR REPLACE FUNCTION update_post_thread_count() 
    RETURNS TRIGGER AS $$
    BEGIN
        UPDATE posts SET threads_count = threads_count + 1 WHERE id = NEW.post_id;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
"""
)


update_post_thread_count_trigger = DDL(
    """\
    CREATE TRIGGER write_post_thread_count 
    AFTER INSERT ON threads
    FOR EACH ROW
    EXECUTE FUNCTION update_post_thread_count()                               

  ;"""
)
event.listen(
    Thread.__table__,
    "after_create",
    update_post_thread_count_func.execute_if(dialect="postgresql"),
)
event.listen(
    Thread.__table__,
    "after_create",
    update_post_thread_count_trigger.execute_if(dialect="postgresql"),
)
