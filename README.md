# Inverse_Design_For_Metalens

绝赞开发中

计划包括三部分：A 基于LumericalFDTD的超透镜单元自动仿真、B 基于Matlab的相位函数优化和远场仿真、C 基于SQLite的数据库建设

希望扩展到基于深度学习的逆向设计

__日志：__

2025/04/11

现在第一阶段的部分已经完全跑通了。而且可以通过在txt文件中修正参数来统一控制输入参数

2025/04/09

就差一点就跑完咯

2025/04/08

完成了昨天的计划，通过四并行把单次计算的时长压缩到了2.7s。明天写子午面计算的相关问题。又回到舒适区咯耶耶耶~

2025/04/07

计划改一下并行的方式，按照波长计算的并行只能并行两组（因为我现在只做两个波长），按照全部数据直接分类似乎更好。今天估计写不完了，写完的部分放在test文件中。

2025/04/05

main2的逻辑和语法调好了，明天测试。matlab转python给自己写晕了。加了一个setting文件，新字体真好用。

2025/04/04

继续执行了昨天的开发计划

2025/04/03

A 目前看最好把优化过程也在python完成，让matlab只剩下阵列仿真的过程，还是尽可能减小大量数据的传输。

2025/04/02

A 目前测试来看，并行会让仿真的时间成本降为百分之七十左右，也就是5秒.最主要的问题还是不确定技术路线，到底是穷举还是前向的遗传算法也罢、粒子群算法也罢，亦或者做好数据库以后用深度学习做逆向设计

2025/03/31

A 确认并行是可用的，目前的方案是同时开启两个波长下的fdtd对象进行并行，用if隔开两个fdtd对象，相当于同时开启两个窗口，避开fdtd不允许并行计算的问题。两边会同时、分别累计数据，在完成计算后统一收录入数据库。这引擎的好处是可以定义为一个函数，其输入和输出的稳定性都较好，不存在“把复杂格式的对象带入并行”的问题，也不需要频繁的建立fdtd窗口，而且每一轮计算后需要重做的结构又少了一个。具体能节省多少时间还没有测试。另，确认可以隐藏GUI窗口计算，并不节省时间，但至少眼前不会心烦。还有一个需要测试的点是连续run/layout是否会在终端堆积大量输出语句

明天一定开始写衍射积分的接口

2025/03/30

B 上传了基于matlab/衍射积分法的仿真函数，使用需加入matlab路径

B 最优化部分已经写好了，没有测试

明天做测试，然后确定一下需要什么包，列一个python的标准开发环境出来。把建立逻辑的部分改为“参数调整”而不是删除重建。今天去玩儿~

2025/03/29

A/B/C 把自动仿真和数据库接起来了，相位优化函数已经可以读取数据库的内容了。阉割了一些之前的设想，选择单个列表里加了四列来表达两个波长下的数据。“先做个垃圾出来”

之后要专注做B的部分，把相位优化函数接入进遗传算法中，再把远场仿真的部分也接入进去。

2025/03/27
A 写了自动仿真程序，思路取自论文*Octave bandwidth photonic fishnet-achromaticmetalens*，但由于目标参数不同，因此需要重新计算数据。现在的问题是数据量实在太大了，可能还得优化

B 把matlab的遗传算法优化相位函数部分上传了

明天开始一定做数据库！

2025/03/27
1.上传了第五周写的数据库模块和一些示例数据

2.基本处理好了自动仿真模块的接口和一些函数，现在已经能进行最基础的仿真啦