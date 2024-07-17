import talib

# list of functions
for name in talib.get_functions():
    print(name)

# dict of functions by group
for group, names in talib.get_function_groups().items():
    print(group)
    for name in names:
        print(f"  {name}")