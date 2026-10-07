def compute_xp(result):
    confidence = str(result.get('confidence','Low')).lower()
    return {'high':75,'medium':60,'low':50}.get(confidence,50)

def level_for_xp(total_xp):
    for threshold, level in [(700,8),(500,7),(350,6),(250,5),(150,4),(75,3),(25,2)]:
        if total_xp >= threshold:
            return level
    return 1
