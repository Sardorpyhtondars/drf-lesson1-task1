from rest_framework.decorators import api_view
from rest_framework.response import Response

from posts.models import Post
from posts.serializers import PostSerializer

@api_view(['GET', 'PUT', 'DELETE'])
def post_list(request):
    if request.method == 'GET':
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(data=serializer.data, status=200)
    else:
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'POST'])
def post_detail(request, pk):
    post = Post.objects.filter(pk=pk).first()
    if not post:
        return Response(status=404)

    if request.method == 'GET':
        serializer = PostSerializer(post)
        return Response(data=serializer.data, status=200)
    elif request.method == 'PUT':
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=201)
        return Response(serializer.errors, status=400)
    elif request.method == 'DELETE':
        post.delete()
        return Response(status=204)
    else:
        return Response(status=405)


