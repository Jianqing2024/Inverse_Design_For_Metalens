from .databaseCleaning import Clean
from .main1 import mainFunction1
from .main2 import mainFunction2

def main_for_EPS():
    Clean()

    # 穷举扫参
    mainFunction1()

    # 最优化计算和远场仿真
    mainFunction2()
