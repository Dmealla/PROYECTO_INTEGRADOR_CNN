from sistema import contar_estable

def simular(ids):
    elegido, estable = None, 0
    for id_ in ids:
        elegido, estable = contar_estable(elegido, estable, id_)
    return elegido, estable          # ← 4 espacios: se ejecuta cuando termina el for
print (simular([4]*15))
print (simular([4,7]*10))
print (simular([4]*10 + [7]+[4]*5))


