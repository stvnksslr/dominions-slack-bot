from asyncio import Semaphore, gather


async def gather_with_concurrency(number_of_tasks, *tasks) -> gather:
    """
    wrapper function to add concurrency limits to a given gather task

    :param number_of_tasks: number of concurrent tasks
    :param tasks: task to be added and managed
    :return:
    """
    semaphore = Semaphore(number_of_tasks)

    async def sem_task(task):
        async with semaphore:
            return await task

    return await gather(*(sem_task(task) for task in tasks))
