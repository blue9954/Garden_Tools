# Garden Tools — Blender Addon

Blender용 게임 아트 제작 보조 도구 모음입니다.  
A collection of game art workflow utilities for Blender.

3D Viewport 사이드바(N 키) → **Garden Tools** 탭에서 사용할 수 있습니다.  
Available in the 3D Viewport sidebar (N key) → **Garden Tools** tab.

---

## Requirements

- Blender **3.0** 이상 / or higher

---

## Installation / 설치 방법

1. 이 저장소에서 `Garden_Tools.py` 다운로드  
   Download `Garden_Tools.py` from this repository

2. Blender → `Edit` > `Preferences` > `Add-ons` > `Install`

3. 다운로드한 파일 선택 후 설치  
   Select the downloaded file and install

4. 애드온 목록에서 **PG Rename** 활성화  
   Enable **PG Rename** in the add-on list

5. 3D Viewport 사이드바(N 키) → **Garden Tools** 탭 확인  
   Open the sidebar (N key) and check the **Garden Tools** tab

---

## Features / 기능

### Rename Panel

게임 아트 워크플로우에서 반복되는 오브젝트·머티리얼 이름 작업을 자동화합니다.  
Automates repetitive object and material naming tasks in game art workflows.

| 기능 / Feature | 설명 / Description |
|---|---|
| **Rename High/Low** | 선택한 Mesh 2개의 폴리곤 수를 비교해 `_high` / `_low`로 리네임하고 컬렉션으로 분리. Renames two selected meshes to `_high` / `_low` based on polygon count and separates them into collections. |
| **Multi Rename** | 선택한 Mesh들을 알파벳순 정렬 후 `이름_01`, `_02`... 형식으로 일괄 리네임. Batch renames selected meshes in alphabetical order as `name_01`, `_02`... |
| **Rename Material by Mesh** | 선택 Mesh의 머티리얼을 `메쉬이름_Mat` 형식으로 리네임. 공유 머티리얼은 자동 복제 처리. Renames materials to `MeshName_Mat`. Shared materials are automatically duplicated. |
| **Clean Up** | Merge by Distance → Delete Loose → Dissolve Degenerate → Apply Rotation/Scale 일괄 처리. Runs mesh cleanup and applies transforms in one click. |
| **Export Low FBX** | 씬 내 `_low` Mesh를 원점 이동 후 개별 FBX로 익스포트. `.blend` 파일 옆 `FBX/` 폴더에 저장. Exports all `_low` meshes as individual FBX files into a `FBX/` folder next to the `.blend` file. |

---

### Smoothing Group Panel

3ds Max의 Smoothing Group과 유사하게 Face 단위로 노멀을 제어합니다.  
Vertex/Edge 선택 상태는 자동으로 Face 선택으로 변환됩니다.

Controls per-face normals similar to 3ds Max Smoothing Groups.  
Vertex/Edge selections are automatically converted to Face selection.

| 기능 / Feature | 설명 / Description |
|---|---|
| **Clear All** | 전체 메쉬의 노멀 초기화 (Flat Shading, Sharp Edge 해제, Custom Normal 제거). Resets all normals on the mesh (Flat Shading, clears sharp edges and custom normal data). |
| **Select Clear** | 선택 Face를 Flat으로 설정하고 해당 영역 내부의 Sharp Edge 제거. Sets selected faces to flat and removes sharp edges within the selection. |
| **Auto Smooth** | 인접 Face 간 각도가 임계값 이상인 Edge에 Sharp 자동 마킹. 각도 입력 시 **실시간 반영** (기본값 45°, 범위 0–180°). Auto-marks sharp edges where the angle between adjacent faces exceeds the threshold. **Updates in real time** as you adjust the angle (default 45°, range 0–180°). |
| **Select Smooth** | 선택 Face 내부를 Smooth 처리하고 경계 Edge에만 Sharp 마킹. Smoothing Group 경계 생성. Smooths the interior of the selected faces and marks only the boundary edges as sharp, creating a Smoothing Group boundary. |

---

## License

This project is released under the **MIT License** — free to use, modify, and distribute for any purpose, including personal and commercial projects.

```
MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Notes 본 프로젝트는 개인 시간에 독립적으로 개발되었습니다. 특정 회사, 프로젝트 또는 내부 파이프라인과는 관련이 없습니다.

제 블로그 주소입니다. https://blog.naver.com/blue9954
