import sqlite3
import os
import re
from tqdm import tqdm
from MetaSet import advancedStructure as ad
from .dataManager import *

def Comput(ids, template, SpectralRange):
    base_dir = os.getcwd()
    DB_PATH = os.path.join(base_dir, "data", "Main.db")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    meta = ad.MetaEngine(parallel=False, template=template, SpectralRange=SpectralRange)
    meta.materialSet()

    for key, values in tqdm(ids.items(), desc="Base structures", unit="group"):
        strClass, baseValue = key[0], key[1]

        cursor.execute("""
        SELECT parameterA, parameterB FROM BaseParameter
        WHERE baseValue = ?
        """, (baseValue,))
        row = cursor.fetchone()
        p, h = row[0], row[1]

        meta.baseBuild(p)

        for id in tqdm(values, desc=f"→ base={baseValue}", unit="sim", leave=False):
            cursor.execute("SELECT * FROM Parameter WHERE ID = ?", (id,))
            row = cursor.fetchone()
            parameter = [row[3], row[4], row[5]]

            meta.structureBuild(strClass, parameter, h)
            meta.dataAcquisition()
            dataInput(meta, id, conn, cursor)
            meta.semi_Reset()

        meta.Reset()
    
    conn.close()

def Jobs_Preparation(meta, group, RUN_PATH):
    dic = {}
    for index, item in enumerate(group):
        meta.Reset()
        name=f'test{index}.fsp'
        Absolute_name = os.path.join(RUN_PATH, name)
        dic[Absolute_name]=item["id"]
        strClass=item["class"]
        p=item["p"]
        h=item["h"]
        paramA=item["paramA"]
        paramB=item["paramB"]
        paramC=item["paramC"]
        
        parameter=parameter = [paramA, paramB, paramC]
        
        meta.baseBuild(p)
        meta.structureBuild(strClass, parameter, h)
        meta.fdtd.save(Absolute_name)
        meta.fdtd.addjob(Absolute_name)
        
    return dic

def STRUCT(meta, group, conn, cursor, RUN_PATH):
    dic=Jobs_Preparation(meta, group, RUN_PATH)
    meta.fdtd.runjobs("FDTD")
    try:
        for Absolute_name, id in dic.items():
            Ex, Trans = StandardDataAcquisition(meta, Absolute_name)
            dataInput_Parallel(Ex, Trans, id, conn, cursor)
    except Exception as e:
        
        if "no d-card named plane" in str(e):
            print("A Jobs issue occurred; attempting to resolve it by resetting.")
            
            try:
                dic=Jobs_Preparation(meta, group, RUN_PATH)
                meta.fdtd.runjobs("FDTD")
                for Absolute_name, id in dic.items():
                    Ex, Trans = StandardDataAcquisition(meta, Absolute_name)
                    dataInput_Parallel(Ex, Trans, id, conn, cursor)
            except Exception as e:
                print("Jobs still encountering issues. Stopped to avoid more complex errors.")
            else:
                print("Issue resolved, rerunning now.")
                
        else:
            raise

def StandardDataAcquisition(meta, name):
    meta.fdtd.load(name)
    Trans = meta.fdtd.transmission("plane")
    Trans = Trans.ravel()

    Ex = meta.fdtd.getresult("point", "Ex")
    Ex = Ex.ravel()

    phase_array = np.angle(np.array(Ex))
    #unwrapped = np.unwrap(phase_array)

    #unwrapped -= 2 * np.pi * np.floor(unwrapped[0] / (2 * np.pi))

    #Ex = unwrapped.tolist()
    Ex = phase_array.tolist()
    Trans = Trans.tolist()

    meta.semi_Reset()
    return Ex, Trans

def ParallelComput(numParallel):
    RUN_PATH = os.getcwd()
    DB_PATH = os.path.join(RUN_PATH, "data", "Main.db")
    SIMULATION_PATH = os.path.join(RUN_PATH, "Temporary_computation_folder")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT wav1, wav5 FROM SpectralParameters")
    wavMin, wavMax = cursor.fetchone()

    meta = ad.MetaEngine(parallel=True, template=True, SpectralRange=[wavMin, wavMax])
    meta.materialSet()

    # 查询所有尚未处理（angleIn1 为 NULL）的行
    cursor.execute("""
        SELECT ID, class, baseValue, parameterA, parameterB, parameterC
        FROM Parameter
        WHERE angleIn1 IS NULL
        ORDER BY ID ASC
    """)
    all_rows = cursor.fetchall()

    if not all_rows:
        print("所有任务均完成，终止任务。")
        conn.close()
        return

    group = []

    for row in tqdm(all_rows, desc="Task", unit="structures"):
        id = row[0]
        strClass = row[1]
        base_value = row[2]
        paramA = row[3]
        paramB = row[4]
        paramC = row[5]

        # 查询 BaseParameter 中的 baseValue 参数
        cursor.execute("SELECT parameterA, parameterB FROM BaseParameter WHERE baseValue = ?", (base_value,))
        base_row = cursor.fetchone()
        if base_row:
            base_paramA = base_row[0]
            base_paramB = base_row[1]
        else:
            base_paramA = base_paramB = None

        # 添加到当前组
        group.append({
            "id": id,
            "class": strClass,
            "paramA": paramA,
            "paramB": paramB,
            "paramC": paramC,
            "p": base_paramA,
            "h": base_paramB
        })

        # 一组满了就执行
        if len(group) == numParallel:
            STRUCT(meta, group, conn, cursor, SIMULATION_PATH)
            group = []

    # 处理剩余不足 numParallel 的最后一组
    if group:
        STRUCT(meta, group, conn, cursor, SIMULATION_PATH)

    conn.close()
    
