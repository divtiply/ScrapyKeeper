import time

from ScrapyKeeper import config

from ScrapyKeeper.app import scheduler, app, agent, JobExecution, db
from ScrapyKeeper.app.spider.model import Project, JobInstance, SpiderInstance, JobRunType, JobPriority
from datetime import datetime


def sync_job_execution_status_job():
    """
    sync job execution running status
    :return:
    """
    for project in Project.query.all():
        agent.sync_job_status(project)
    app.logger.debug('[sync_job_execution_status]')


def sync_spiders():
    """
    sync spiders
    :return:
    """
    for project in Project.query.all():
        spider_instance_list = agent.get_spider_list(project)
        SpiderInstance.update_spider_instances(project.id, spider_instance_list)
    app.logger.debug('[sync_spiders]')


def run_spider_job(job_instance_id):
    """
    run spider by scheduler
    :param job_instance_id:
    :return:
    """
    try:
        job_instance = JobInstance.find_job_instance_by_id(job_instance_id)
        agent.start_spider(job_instance)
        app.logger.info('[run_spider_job][project:%s][spider_name:%s][job_instance_id:%s]' % (
            job_instance.project_id, job_instance.spider_name, job_instance.id))
    except Exception as e:
        app.logger.error('[run_spider_job] ' + str(e))


def reload_runnable_spider_job_execution():
    """
    add periodic job to scheduler
    :return:
    """
    running_job_ids = set([job.id for job in scheduler.get_jobs()])
    # app.logger.debug('[running_job_ids] %s' % ','.join(running_job_ids))
    available_job_ids = set()
    # add new job to schedule
    for job_instance in JobInstance.query.filter_by(enabled=0, run_type="periodic").all():
        job_id = "spider_job_%s:%s" % (job_instance.id, int(time.mktime(job_instance.date_modified.timetuple())))
        available_job_ids.add(job_id)
        if job_id not in running_job_ids:
            try:
                scheduler.add_job(run_spider_job,
                                  args=(job_instance.id,),
                                  trigger='cron',
                                  id=job_id,
                                  minute=job_instance.cron_minutes,
                                  hour=job_instance.cron_hour,
                                  day=job_instance.cron_day_of_month,
                                  day_of_week=job_instance.cron_day_of_week,
                                  month=job_instance.cron_month,
                                  second=0,
                                  max_instances=999,
                                  misfire_grace_time=60 * 60,
                                  coalesce=True)
            except Exception as e:
                app.logger.error(
                    '[load_spider_job] failed {} {},may be cron expression format error '.format(job_id, str(e)))
            app.logger.info('[load_spider_job][project:%s][spider_name:%s][job_instance_id:%s][job_id:%s]' % (
                job_instance.project_id, job_instance.spider_name, job_instance.id, job_id))
    # remove invalid jobs
    for invalid_job_id in filter(lambda job_id: job_id.startswith("spider_job_"),
                                 running_job_ids.difference(available_job_ids)):
        scheduler.remove_job(invalid_job_id)
        app.logger.info('[drop_spider_job][job_id:%s]' % invalid_job_id)


def run_spiders_by_algorithm():
    """
    Run all the spiders when needed
    :return:
    """
    for project in Project.query.all():
        _run_spiders_for_project(project)
    app.logger.debug('[run_spiders_by_algorithm]')


def _run_spiders_for_project(project: Project):
    """
    Run all the spiders for the current project
    :param project:
    :return:
    """
    # grab the list with all the spiders in the project
    spider_list = [spider_instance.to_dict() for spider_instance in
                   SpiderInstance.query.filter_by(project_id=project.id).order_by(
                       SpiderInstance.spider_name).all()]

    # compute the current running load
    current_run_load = _get_current_run_load(project.id)

    # gather a list with all the spiders
    spiders_by_avg_run_load = [{'spider_id': spider['spider_instance_id'],
                                'spider_name': spider['spider_name'],
                                'avg_load': _get_spider_average_run_stats(project.id, spider['spider_instance_id'])}
                               for spider in spider_list]
    # sort the list from the one with least requests to the one with most
    spiders_by_avg_run_load = sorted(spiders_by_avg_run_load, key=lambda i: i['avg_load'])

    # gather a list of active spiders only
    active_spiders_avg_run_load = [spider['avg_load'] for spider in spiders_by_avg_run_load if spider['avg_load'] > 0]
    # compute the avg load time for those spiders
    active_spiders_avg_run_load = sum(active_spiders_avg_run_load) / max(len(active_spiders_avg_run_load), 1)
    active_spiders_avg_run_load = active_spiders_avg_run_load if active_spiders_avg_run_load > 0 \
        else config.DEFAULT_LOAD_TO_ADD

    # run the spiders that we have to run
    for spider_to_run in spiders_by_avg_run_load:
        spider_avg_load = spider_to_run['avg_load'] if spider_to_run['avg_load'] > 0 else \
                active_spiders_avg_run_load

        if _spider_should_run(spider_to_run['spider_id'], spider_avg_load, current_run_load):
            _run_spider(spider_to_run['spider_name'], project.id)
            current_run_load += spider_avg_load

        if current_run_load >= config.MAX_REQUESTS_PER_MINUTE_ALLOWED:
            # the load is already to the max, we can't add anything
            break


def _get_current_run_load(project_id) -> float:
    """
    Get the current work load for all the jobs
    :param project_id:
    :return:
    """
    running_jobs = JobExecution.list_running_jobs(project_id)

    running_avg = []
    for running_job in running_jobs:
        spider_name = running_job['job_instance']['spider_name']
        spider_id = SpiderInstance.get_spider_by_name_and_project_id(spider_name, project_id).id

        running_avg.append(_get_spider_average_run_stats(project_id, spider_id))

    total_load = sum(running_avg) / max(len(running_avg), 1)

    return total_load


def _get_spider_average_run_stats(project_id, spider_id) -> float:
    # grab only execution that finished successfully
    execution_list = JobExecution.list_spider_stats(project_id, spider_id)
    # keep only the latest 10 runs
    execution_list = execution_list[-10:]
    # keep only the runs from the current project (for some reason it returns all the projects)
    execution_list = [execution for execution in execution_list if execution['project_id'] == project_id]

    requests_counters = [execution['requests_count'] for execution in execution_list]
    average_requests = sum(requests_counters) / max(len(requests_counters), 1)

    execution_seconds = [(datetime.strptime(execution['end_time'], '%Y-%m-%d %H:%M:%S')
                          - datetime.strptime(execution['start_time'], '%Y-%m-%d %H:%M:%S')).total_seconds()
                         for execution in execution_list]
    # get average run time in minutes
    average_seconds = sum(execution_seconds) / max(len(execution_seconds), 1) / 60

    avg_req_per_min = average_requests / max(average_seconds, 1)

    return avg_req_per_min


def _run_spider(spider_name, project_id):
    """
    Run a spider
    :param spider_name: 
    :param project_id: 
    :return: 
    """
    job_instance = JobInstance()
    job_instance.project_id = project_id
    job_instance.spider_name = spider_name
    job_instance.priority = JobPriority.NORMAL
    job_instance.run_type = JobRunType.ONETIME
    job_instance.overlapping = False
    job_instance.enabled = -1

    # settings for tempering the requests
    requests_concurrency_arg = _set_throttle_args(spider_name, project_id)
    job_instance.spider_arguments = requests_concurrency_arg

    db.session.add(job_instance)
    db.session.commit()

    agent.start_spider(job_instance)


def _set_throttle_args(spider_name, project_id):
    """
    Find the AUTOTHROTTLE_TARGET_CONCURRENCY for this request
    :param spider_id:
    :param project_id:
    :return:
    """
    spider_instance = SpiderInstance.query.filter_by(spider_name=spider_name, project_id=project_id).first()

    # grab only execution that finished successfully
    execution_list = JobExecution.list_spider_stats(project_id, spider_instance.id)
    # keep only the latest 10 runs
    execution_list = execution_list[-10:]
    # keep only the runs from the current project (for some reason it returns all the projects)
    execution_list = [execution for execution in execution_list if execution['project_id'] == project_id]

    execution_seconds = [(datetime.strptime(execution['end_time'], '%Y-%m-%d %H:%M:%S')
                          - datetime.strptime(execution['start_time'], '%Y-%m-%d %H:%M:%S')).total_seconds()
                         for execution in execution_list]
    # get average run time in minutes
    average_mins = sum(execution_seconds) / max(len(execution_seconds), 1) / 60

    if average_mins == 0:
        # when we don't have any info about past runs
        return None

    time_spent_ratio = float(1440 / average_mins)  # the ratio reported to 1 day
    # now we'll have to only keep the number with a min of .5 and a max of 10
    time_spent_ratio = max(time_spent_ratio, 0.5)
    time_spent_ratio = min(time_spent_ratio, 10)
    autothrottle_to_set = config.DEFAULT_AUTOTHROTTLE_MAX_CONCURRENCY / time_spent_ratio

    requests_concurrency_arg = "setting=AUTOTHROTTLE_TARGET_CONCURRENCY={}".format(autothrottle_to_set)

    return requests_concurrency_arg


def _spider_should_run(spider_id, spider_avg_load, current_run_load):
    """
    Check if this spider should run now
    :param spider_id:
    :param current_run_load:
    :return:
    """
    spider = SpiderInstance.query.get(spider_id)
    last_run = JobExecution.get_last_spider_execution(spider.id, spider.project_id)

    if last_run is not None and last_run > datetime.today().replace(hour=0, minute=0, second=0):
        # test the crawler didn't run today
        return False

    pending_instances = JobExecution.get_pending_jobs_by_spider_name(spider.spider_name, spider.project_id)
    if len(pending_instances):
        # check that another instance of the same crawler is in pending
        return False

    running_instances = JobExecution.get_running_jobs_by_spider_name(spider.spider_name, spider.project_id)
    if len(running_instances):
        # check that another instance of the same crawler is running
        return False

    if spider.auto_schedule is False:
        # check if the marker from the DB allows auto scheduling
        return False

    if current_run_load + spider_avg_load > config.MAX_REQUESTS_PER_MINUTE_ALLOWED:
        # check that the load is still under control
        return False

    return True
