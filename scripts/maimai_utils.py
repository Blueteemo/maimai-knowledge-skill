"""
maimai_utils.py — 舞萌DX扩展工具
提供水鱼API的额外功能：拟合难度查询、歌曲封面获取。

依赖: pip install requests
"""

import requests
import sys


# ===== 封面图获取 =====

def get_cover_len5_id(mid: int) -> str:
    """
    将歌曲ID转换为封面图所需的ID字符串。
    
    水鱼封面API直接用原始数字ID即可，但部分旧歌（如ID<=10000）需要补0至5位。
    对于ID区间10001~11000的歌曲，DX谱面与SD谱面共用封面，需减去10000。
    """
    mid = int(mid)
    if 10000 < mid <= 11000:
        mid -= 10000
    return f"{mid:05d}"


def get_cover_url(mid: int) -> str:
    """
    获取歌曲封面图的URL。
    
    封面URL格式: https://www.diving-fish.com/covers/{cover_id}.png
    水鱼封面API支持直接使用原始数字ID，也可使用补零后的5位ID。
    """
    cover_id = get_cover_len5_id(mid)
    return f"https://www.diving-fish.com/covers/{cover_id}.png"


def download_cover(mid: int, save_path: str = None) -> bytes:
    """
    下载歌曲封面图。
    
    参数:
        mid: 歌曲ID
        save_path: 可选，保存到本地文件路径
    返回:
        图片的二进制数据
    """
    url = get_cover_url(mid)
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    
    if save_path:
        with open(save_path, "wb") as f:
            f.write(resp.content)
    
    return resp.content


# ===== 拟合难度查询 =====

def get_chart_stats() -> dict:
    """
    获取所有谱面的拟合难度数据。
    
    返回:
        {
            "charts": {song_id: [谱面数据...]},  # 按song_id索引
            "diff_data": {difficulty: 统计数据}   # 按难度等级索引
        }
    
    每个谱面数据包含:
        - cnt: 样本数量
        - diff: 官标难度等级
        - fit_diff: 拟合难度（浮点数，比官标定数更精确）
        - avg: 平均达成率
        - avg_dx: 平均DX分数
        - std_dev: 标准差
        - dist: 评级分布 [d, c, b, bb, bbb, a, aa, aaa, s, sp, ss, ssp, sss, sssp]
        - fc_dist: FC分布 [非, fc, fcp, ap, app]
    """
    url = "https://www.diving-fish.com/api/maimaidxprober/chart_stats"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.json()


def get_song_chart_stats(song_id: int) -> list:
    """
    获取指定歌曲的拟合难度数据。
    
    参数:
        song_id: 歌曲ID
    
    返回:
        该歌曲所有谱面的拟合难度数据列表
    """
    data = get_chart_stats()
    charts = data.get("charts", {})
    return charts.get(str(song_id), [])


def format_chart_stats(song_id: int, song_title: str = "") -> str:
    """
    将歌曲的拟合难度数据格式化为可读文本。
    """
    stats = get_song_chart_stats(song_id)
    if not stats:
        return f"⚠️ 未找到歌曲 ID {song_id} 的拟合难度数据"
    
    title_info = f" **{song_title}**" if song_title else ""
    lines = [f"📊 拟合难度 {title_info}(ID: {song_id}):"]
    
    for s in stats:
        diff = s.get("diff", "?")
        fit_diff = s.get("fit_diff", "?")
        avg = s.get("avg", "?")
        cnt = s.get("cnt", "?")
        lines.append(f"  Lv.{diff} → 拟合定数 {fit_diff:.2f} | 平均达成率 {avg:.2f}% | 样本 {cnt}人")
    
    return "\n".join(lines)


def get_song_fit_diff(song_id: int, level_index: int = None) -> list:
    """
    获取指定歌曲指定难度的拟合难度。
    
    参数:
        song_id: 歌曲ID
        level_index: 可选，谱面索引 (0=basic, 1=advanced, 2=expert, 3=master, 4=remaster)
                     不传则返回所有难度
    
    返回:
        [(level_index, diff, fit_diff, avg), ...]
    """
    stats = get_song_chart_stats(song_id)
    results = []
    
    for s in stats:
        idx = s.get("level_index", 0)
        if level_index is not None and idx != level_index:
            continue
        results.append((idx, s.get("diff"), s.get("fit_diff"), s.get("avg")))
    
    return results


# ===== 测试入口 =====
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python maimai_utils.py <命令> [参数...]")
        print("命令:")
        print("  cover <歌曲ID> [保存路径]  — 下载歌曲封面")
        print("  fitdiff <歌曲ID>           — 查询拟合难度")
        print("  stats                     — 获取全部拟合难度统计概览")
        print("")
        print("示例:")
        print("  python maimai_utils.py cover 38")
        print("  python maimai_utils.py fitdiff 38")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "cover":
        mid = int(sys.argv[2])
        save_path = sys.argv[3] if len(sys.argv) > 3 else None
        data = download_cover(mid, save_path)
        print(f"✅ 封面已下载 ({len(data)} bytes)")
        print(f"   URL: {get_cover_url(mid)}")
        
    elif cmd == "fitdiff":
        mid = int(sys.argv[2])
        title = sys.argv[3] if len(sys.argv) > 3 else ""
        print(format_chart_stats(mid, title))
        
    elif cmd == "stats":
        data = get_chart_stats()
        charts = data.get("charts", {})
        diff_data = data.get("diff_data", {})
        print(f"📊 拟合难度数据概览:")
        print(f"   歌曲谱面数: {len(charts)}")
        print(f"   难度等级统计: {len(diff_data)} 个等级")
        
    else:
        print(f"❌ 未知命令: {cmd}")
