# AccessTrace Campus Demo Script

目标时长：约 2 分 30 秒。操作提示用中文，口播保持英文。

## 0:00-0:25 — Problem

**操作：** 打开首页，先停留在标题、责任边界和三个指标处。

**English narration:**

> Campus maps usually optimize distance, but they rarely show whether accessibility evidence is complete. AccessTrace Campus is an evidence-first outdoor routing prototype for people with reduced mobility. It proposes a candidate route, exposes missing map evidence, and never claims that a route is safe, ADA-compliant, or field-verified.

## 0:25-0:55 — Real route

**操作：** 在左侧确认起点为 `University Commons`，终点为 `Hall of Sciences`。指向 636 米、17% evidence coverage 和 48 unknown segments。

**English narration:**

> This example uses a real OpenStreetMap extract around Drew University. The deterministic route is 636 meters. Only 17 percent of its segments contain an accessibility-related tag, so 48 segments remain explicitly unknown instead of being treated as accessible.

## 0:55-1:30 — Evidence ledger

**操作：** 向下滚动到 `Route evidence`，展示 `wheelchair`、`kerb`、`surface`、`incline`、`smoothness` 和 `ramp:wheelchair` 列。

**English narration:**

> The evidence ledger shows exactly what the map knows for every segment. The routing core excludes explicit barriers such as wheelchair-no, raised kerbs, and steps without a designated wheelchair ramp. Missing tags stay visible as unknown. This makes the system inspectable rather than hiding uncertainty behind a single accessibility score.

## 1:30-2:05 — Temporary barrier and reroute

**操作：** 在 `Route segment` 选择 `Segment 3 · footway`，reason 保持 `construction`，expiry 保持 30 minutes，点击 `Add temporary barrier`。页面刷新后指向新的 673 米距离和左侧 active barrier 计数 1。

**English narration:**

> Now I will add a temporary construction barrier to the third route segment. The report exists only in this browser session and expires after 30 minutes. The route recalculates to 673 meters, a 37-meter detour, while preserving the same evidence boundary.

## 2:05-2:30 — Technical close

**操作：** 指向地图和底部 OpenStreetMap attribution；最后点击 `Clear temporary barriers` 恢复原路线。

**English narration:**

> Under the hood, the prototype uses standard-library OSM parsing, deterministic Dijkstra routing, expiring barriers, and regression tests. The next step is verified entrance mapping and field validation with campus accessibility teams. AccessTrace does not replace on-site judgment; it makes the evidence and uncertainty visible before a person decides.

## 录制前检查

1. 运行 `python scripts/download_osm.py`，再运行 `streamlit run app.py`。
2. 确认默认路线为约 636 米，证据表第三段 ID 为 `707993174:707993208`。
3. 清除所有临时障碍，关闭无关通知，浏览器缩放保持 100%。
4. 录制时只展示浏览器，不展示本地路径、终端历史、邮箱或账号信息。
