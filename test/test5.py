a = {"arg1": [1, 2, 3, 4, 5, {"arg2": [6, 7, 8, 9]}]}
print(a.get('arg1', []).index())
