def get_average_rating(id, model):
    ratings = model.objects.get(id=id).ratings.all()
    quantity = model.objects.get(id=id).ratings.count()
    summary = 0

    for rate in ratings:
        summary += rate.rating
    if summary == 0:
        return summary

    summary = round(summary/quantity)
    return summary
