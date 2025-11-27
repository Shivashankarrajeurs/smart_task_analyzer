from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TaskSerializer
from . import scoring  # make sure this is your new scoring.py

class AnalyzeTasksView(APIView):
    def post(self, request):
        data = request.data
        if not isinstance(data, list):
            return Response({"detail": "Expected a JSON array of tasks."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TaskSerializer(data=data, many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        tasks = serializer.validated_data

        # Convert dependencies to accept IDs as integers or strings
        for idx, task in enumerate(tasks):
            if "id" not in task:
                task["id"] = str(idx)  # auto-assign string ID if not present

        try:
            scored = scoring.score_tasks(tasks)  # <--- use score_tasks, not calculate_priority_scores
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": "Internal error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(scored, status=status.HTTP_200_OK)


class SuggestTasksView(APIView):
    def get(self, request):
        tasks_param = request.query_params.get('tasks', None)
        if tasks_param:
            import json
            try:
                tasks = json.loads(tasks_param)
            except json.JSONDecodeError:
                return Response({"detail": "Invalid JSON in 'tasks' query parameter."}, status=status.HTTP_400_BAD_REQUEST)

            serializer = TaskSerializer(data=tasks, many=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            for idx, task in enumerate(tasks):
                if "id" not in task:
                    task["id"] = str(idx)

            try:
                scored = scoring.score_tasks(serializer.validated_data)
            except ValueError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"detail": "Internal error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            if not hasattr(scoring, "LAST_ANALYZED") or not scoring.LAST_ANALYZED:
                return Response({"detail": "No previously analyzed tasks found. POST /api/tasks/analyze/ first or pass tasks as query param."}, status=status.HTTP_400_BAD_REQUEST)
            scored = scoring.LAST_ANALYZED

        top3 = scored[:3]
        return Response(top3, status=status.HTTP_200_OK)
