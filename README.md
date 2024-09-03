# Deadlock 台灣繁體

原翻譯 https://github.com/233Isaac/DeadlockSC  
這裡是 Fork 修改為台灣用語

### 功能

- 自動偵測路徑
- 一鍵安裝漢化

### 使用方法

1. [點此下載](https://github.com/cycleapple/DeadlockTC/releases/download/v1.2.0/Deadlock_Updater.zip)
2. 解壓縮 `Deadlock繁體漢化更新器` 資料夾 (建議要有資料夾包起來，因為會產生其他檔案)
3. 打開 `Deadlock繁體漢化更新器.exe`
4. 點擊 `自動偵測路徑`
5. 點擊 `安裝/更新漢化`

未來更新點擊 `安裝/更新漢化` 即可，不須重新下載更新器。


## 自行建置更新器

若您想自行建置更新器，請按照以下步驟操作：

#### 1. 安裝 Python 和 依賴包

確保您已經安裝了 Python（建議使用 Python 3.8 或以上版本）。接著，請使用下列指令建立虛擬環境並安裝依賴包：

```bash
# 在專案目錄中建立虛擬環境
python -m venv .venv

# 啟動虛擬環境
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 安裝依賴包
pip install -r requirements.txt
```

#### 2. 建置更新器
```bash
# 生成可執行檔案
pyinstaller --onefile --noconsole --icon=src/updater/resources/icon.ico Updater.spec
```
編譯完成後，`dist/` 資料夾下會生成 `updater.exe`。

#### 3. 使用自定義圖示 (Optional)
若您需要更改圖示，請將自定義的 `icon.ico` 放入 `src/updater/resources/` 目錄，並更新 `Updater.py` 中的圖示路徑。

## 注意事項

- 使用虛擬環境來管理依賴包，避免影響系統全局的 Python 安裝。
- 在建置前，請確保所有依賴包已經列入 requirements.txt 中。
- 對於開發者而言，熟悉 PyInstaller 的基本使用方式是必要的，尤其是在調試和配置不同選項時。