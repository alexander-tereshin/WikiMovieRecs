
from django.shortcuts import render
from django.http import JsonResponse
from .tasks import train_model_and_save, get_similar_articles, check_model_files
from celery.result import AsyncResult


def index(request):
    result = check_model_files.delay()
    task_result = result.get()
    if task_result == "model_ready":
        return render(request, "main/index.html")
    return render(request, "main/need_train.html")


def train(request):
    task = train_model_and_save.apply_async()
    return render(request, "main/train.html", {"task_id": task.id})


def get_similar(request):
    try:
        url = request.GET["url"]
        cnt = int(request.GET["cnt"])
    except Exception as e:
        return render(request, "main/error.html", {"error": str(e)})

    task = get_similar_articles.apply_async(args=[url, cnt])

    return JsonResponse({"task_id": task.id, "status": "Task queued"})


def task_status(request, task_id):
    task = AsyncResult(task_id)
    if task.state == "PENDING":
        response = {"status": "Task is being processed or not found"}
    elif task.state == "SUCCESS":
        try:
            if not task.result:
                return JsonResponse(
                    {"status": "Model has been trained."}
                )
            films, query_film = task.result
            context = {"films": films, "query_film": query_film}
            return render(request, "main/get_similar.html", context)
        except Exception as e:
            response = {"status": "Error retrieving result", "error": str(e)}
    elif task.state == "RETRY":
        response = {"status": "Task is being retried..."}
    elif task.state == "STARTED":
        response = {"status": "Task has started processing."}
    else:
        response = {"status": f"Task is in unknown state: {task.state}"}

    return JsonResponse(response)