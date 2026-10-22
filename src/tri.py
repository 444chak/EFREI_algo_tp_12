def tri_fusion(elements, key, decroissant=False):
    """Tri fusion stable. Temps O(n log n), espace O(n). Renvoie une nouvelle liste."""

    return (
        list(elements)
        if len(elements) <= 1
        else _fusionner(
            tri_fusion(elements[: len(elements) // 2], key, decroissant),
            tri_fusion(elements[len(elements) // 2 :], key, decroissant),
            key,
            decroissant,
        )
    )


def _fusionner(left, right, key, decroissant):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        a, b = key(left[i]), key(right[j])
        if (a >= b) if decroissant else (a <= b):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
