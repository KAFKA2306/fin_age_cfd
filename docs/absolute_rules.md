コメント不要です。
KEYはwindows10 環境変数にcmdから一時的かつ恒久的に設定するようにしましょう。
全体のアーキテクチャを考えて、実装しましょう。
src以下にpyを作っていく
output以下に、フォルダ分けして保存していく
configファイル内で、BASE_DIR =fr"E:/e/d", OUTPUT_DIR= os.path.join(BASE_DIR, "output")のようにフォルダを設定していく。output内には直接ファイルを保存せずに、データの種類ごとにディレクトリを作って保存する。一連のディレクトリはconfigで生成する。
コメント不要
明瞭に
import 任意のsrc以下のpyファイル名の形でimportする
from . は全て不要
データの入出力はparquet形式にする。
時間colは標準的なdatetime形式でindexに設定する
