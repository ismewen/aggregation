from celery_app import celery


@celery.task()
def celery_test():
    print("this is an celery test")
