from rest_framework import serializers
from .models import *
from .utils import get_average_rating


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VacancyImage
        fields = ('image', )


class VacancySerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.email')

    class Meta:
        model = Vacancy

        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['images'] = ImageSerializer(instance.images.all(), many=True).data
        action = self.context.get('action')
        if action == 'list':
            representation.pop('description')
            representation['likes'] = instance.likes.count()
            representation['rating'] = get_average_rating(representation.get("id"), Vacancy)
        elif action == 'retrieve':
            representation['comments'] = CommentSerializer(instance.comments.all(), many=True).data
            representation['likes'] = instance.likes.count()
            representation['rating'] = RatingSerializer(instance.ratings.all(), many=True).data
        return representation

    def create(self, validated_data):
        request = self.context.get('request')
        images_data = request.FILES
        job = Vacancy.objects.create(author=request.user, **validated_data)
        for image in images_data.getlist('images'):
            VacancyImage.objects.create(image=image, job=job)
        return job

    def update(self, instance, validated_data):
        request = self.context.get('request')
        for key, value in validated_data.items():
            setattr(instance, key, value)
        images_data = request.FILES
        instance.images.all().delete()
        for image in images_data.getlist('images'):
            VacancyImage.objects.create(image=image, job=instance)
        return instance


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.email')

    class Meta:
        model = Comment
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        action = self.context.get('action')
        if action == 'list':
            representation['comments'] = instance.comments.count()
        elif action == 'retrieve':
            representation['comments'] = CommentSerializer(instance.comments.all(), many=True).data
        return representation

    def create(self, validated_data):
        request = self.context.get('request')
        comment = Comment.objects.create(
            author=request.user, **validated_data
        )
        return comment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', )


class RatingSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.email')

    class Meta:
        model = Rating
        fields = '__all__'

    def create(self, validated_data):
        request = self.context.get('request')
        email = request.user
        vacancy = validated_data.get('vacancy')

        if Rating.objects.filter(author=email, vacancy=vacancy):
            rating = Rating.objects.get(author=email, vacancy=vacancy)
            return rating

        rating = Rating.objects.create(author=request.user, **validated_data)
        return rating