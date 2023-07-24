from factory.infofactory import *


def task1():
    fact = InfoFactory()
    # 显示原始父级链路
    key_name = input("Name: ")
    allitem = list(fact.get_structures_by_name(key_name))
    for i, item in enumerate(allitem):
        print(i, item.value, item.name)
    numorder = input("Num of order (base-1): ")
    numorder = int(numorder)
    pval = allitem[numorder].pval
    for item in fact.patrilineal_link(pval):
        print(item.value, item.name)


def task2():
    new_name = input("Name:")
    sysid = int(input("System: "))
    pval = int(input("Parent value: "))
    newis_parent = int(input("Is_parent: "))

    fact = InfoFactory()
    new_sturc = fact.generate_new_sturcture(sysid, newis_parent, 0)
    new_sturc.name = new_name
    new_sturc.pval = pval
    print(new_sturc)
    sure = input("Are you sure(y/n)?\n")
    if sure == "y":
        fact.create_structure(new_sturc)


if __name__ == '__main__':
    task2()
