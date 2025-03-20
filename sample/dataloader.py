import os
import numpy as np
import pandas as pd
import logging
from typing import Dict, Optional, List


logging.basicConfig(
    filename="logs/dataloader.log",
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DefaultDataLoader:
    def __init__(self, input_file: str, device_name: str, **kwargs):
        self.input_file = input_file
        self.device_name = device_name
        self.df = None
        self.logger = logger
        self.kwargs = kwargs

    def load_data(self) -> Optional[pd.DataFrame]:
        try:
            file_extension = os.path.splitext(self.input_file)[1]
        except Exception:
            self.logger.error("Invalid file path")
            return None
        if file_extension == ".csv":
            self.df = pd.read_csv(self.input_file)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        return self.df

    def handle_missing_value(self, strategy: str = "None") -> pd.DataFrame:
        """
        欠損値の処理
        Args:
            strategy (str): 処理方法 ('ffill', 'bfill', 'drop', 'interpolate', 'None')
        Returns:
            pd.DataFrame: 処理後のデータフレーム
        """

        try:
            if strategy == "ffill":
                self.df = self.df.fillna(method="ffill")
            elif strategy == "bfill":
                self.df = self.df.fillna(method="bfill")
            elif strategy == "drop":
                self.df = self.df.dropna()
            elif strategy == "interpolate":
                self.df = self.df.interpolate()
            elif strategy == "None":
                pass
            else:
                raise ValueError(f"Invalid strategy: {strategy}")

            self.logger.info("Applied missing value handling strategy: %s", strategy)

        except Exception as e:
            self.logger.error("Error handling missing values: %s", str(e))
            raise

        return self.df

    def convert_dtypes(self, dtype_dict: dict) -> pd.DataFrame:
        """
        データ型の変換
        Args:
            dtype_dict (dict): カラム名とデータ型の辞書
        Returns:
            pd.DataFrame: 処理後のデータフレーム
        """
        try:
            self.df = self.df.astype(dtype_dict)
            self.logger.info("Converted data types according to specified schema")
            return self.df

        except Exception as e:
            self.logger.error("Error converting data types: %s", str(e))
            raise

    def validate_data(self, validation_rules: Optional[Dict] = None) -> bool:
        """
        データの検証
        Args:
            validation_rules (Optional[Dict]): 検証ルール
                {
                    'column_name': {
                        'min': minimum_value,
                        'max': maximum_value,
                        'allowed_values': list_of_allowed_values
                    }
                }
        Returns:
            bool: 検証結果
        """
        if validation_rules is None:
            return True

        try:
            for column, rules in validation_rules.items():
                if 'min' in rules:
                    assert self.df[column].min() >= rules['min']
                if 'max' in rules:
                    assert self.df[column].max() <= rules['max']
                if 'allowed_values' in rules:
                    assert self.df[column].isin(rules['allowed_values']).all()

            self.logger.info("Data validation passed successfully")
            return True

        except AssertionError as e:
            self.logger.error("Data validation failed: %s", str(e))
            return False
        except Exception as e:
            self.logger.error("Error during data validation: %s", str(e))
            raise

    def save_cleaned_data(self, output_file: str) -> None:
        """
        クリーニング済みデータの保存
        Args:
            output_file (str): 出力ファイルパス
        """
        try:
            file_ext = os.path.splitext(output_file)[1].lower()
            if file_ext == '.csv':
                self.df.to_csv(output_file, index=False)
            elif file_ext in ['.xlsx', '.xls']:
                self.df.to_excel(output_file, index=False)
            else:
                raise ValueError(f"Unsupported output format: {file_ext}")

            self.logger.info("Successfully saved cleaned data to %s", output_file)

        except Exception as e:
            self.logger.error("Error saving cleaned data: %s", str(e))
            raise

    def ret_data(self) -> Dict:
        """
        データフレームの取得
        Returns:
            {"input_file": self.input_file, "device_name": self.device_name, "data": self.df}
        """
        return {"input_file": self.input_file, "device_name": self.device_name, "data": self.df}

    def process(self, cleaning_config: dict) -> pd.DataFrame:
        """
        データの前処理
        Args:
            cleaning_config (dict): 前処理設定
                {
                    'missing_values': 'drop',
                    'data_types': {
                        'column_name': 'int'
                    },
                    'validation_rules': {
                        'column_name': {
                            'min': minimum_value,
                            'max': maximum_value,
                            'allowed_values': list_of_allowed_values
                        }
                    }
                }
        Returns:
            pd.DataFrame: 前処理後のデータフレーム
        """
        try:
            self.load_data()
            if 'missing_values' in cleaning_config:
                self.handle_missing_value(cleaning_config.get('missing_values', 'None'))

            if 'data_types' in cleaning_config:
                self.convert_dtypes(cleaning_config['data_types'])

            if 'validation_rules' in cleaning_config:
                self.validate_data(cleaning_config['validation_rules'])

            self.logger.info("Data processing completed successfully")
            return self.df

        except Exception as e:
            self.logger.error("Error processing data: %s", str(e))
            raise

# データ形式名：B1500aText2CSVDataLoader


class Sample2DataLoader(DefaultDataLoader):
    def __init__(self, input_file: str, device_name: str):
        """
        初期化
        Args:
            input_file (str): 入力ファイルのパス
            device_name (str): デバイス名
        """
        super().__init__(input_file, device_name)
        self.header_info = {}
        self.data_start_index = None

    def load_data(self) -> pd.DataFrame:
        """B1500Atext2csv形式のファイルを読み込み、ヘッダー解析とデータ抽出を行う"""
        try:
            with open(self.input_file, 'r') as f:
                raw_data = f.readlines()

            # ヘッダー解析
            self._parse_header(raw_data)

            # データ抽出
            self.df = self._extract_data(raw_data)

            self.logger.info(f"Successfully loaded data from {self.input_file}")
            return self.df

        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            raise

    def _parse_header(self, raw_data: List[str]) -> None:
        """ヘッダー部分の解析"""
        try:
            for i, line in enumerate(raw_data):
                if line.startswith('DataName'):
                    self.data_start_index = i
                    break

                if line.startswith('TestParameter') or \
                   line.startswith('MetaData') or \
                   line.startswith('AnalysisSetup'):
                    key, value = line.strip().split(',', 1)
                    self.header_info[key] = value

            if self.data_start_index is None:
                raise ValueError("Data section not found")

        except Exception as e:
            self.logger.error(f"Error parsing header: {str(e)}")
            raise

    def _extract_data(self, raw_data: List[str]) -> pd.DataFrame:
        """測定データ部分の抽出"""
        try:
            # カラム名の取得
            columns = [col.strip() for col in raw_data[self.data_start_index].strip().split(',')[1:]]

            # データの抽出
            data_lines = []
            for line in raw_data[self.data_start_index + 1:]:
                if line.startswith('DataValue'):
                    values = line.strip().split(',')[1:]
                    # 空の文字列を0に変換
                    values = [v if v.strip() else '0' for v in values]
                    data_lines.append(values)

            # DataFrameの作成
            df = pd.DataFrame(data_lines, columns=columns)

            # データ型の変換
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            return df

        except Exception as e:
            self.logger.error(f"Error extracting measurement data: {str(e)}")
            raise

    def validate_data(self, validation_rules: Optional[Dict] = None) -> bool:
        """
        データの検証（オーバーライド用）
        """
        pass


# データ形式名：B1500aSingleFileCSVDataLoader
class Sample3DataLoader(DefaultDataLoader):
    def __init__(self, input_file: str, device_name: str = "B1500A", **kwargs):
        """
        初期化

        Args:
            input_file: 解析するファイルのパス
            device_name: デバイス名
        """
        super().__init__(input_file, device_name, **kwargs)
        self.header_info = {}
        self.columns = []
        self.raw_data = []
        self.auto_analysis_start = -1
        self.df = None
        self.data_section_start = -1

    def load_data(self) -> Optional[pd.DataFrame]:
        """
        ファイルを解析して読み込む

        Returns:
            pd.DataFrame: 読み込んだデータフレーム
        """
        try:
            self._read_file()
            self._parse_header()
            self._extract_data()
            self.logger.info("Successfully parsed file: %s", self.input_file)
            return self.df
        except Exception as e:
            self.logger.error("Error parsing file %s: %s", self.input_file, str(e))
            raise

    def _read_file(self) -> None:
        """ファイルを読み込む"""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                self.raw_data = f.readlines()
            self.logger.info("File read successfully: %s", self.input_file)
        except Exception as e:
            self.logger.error("Error reading file: %s", str(e))
            raise

    def _parse_header(self) -> None:
        """
        ヘッダー情報を解析する
        - AutoAnalysisまでの行をヘッダーとする
        - 行の形式は「キー,値」
        """
        try:
            for i, line in enumerate(self.raw_data):
                line = line.strip()

                # AutoAnalysis行でヘッダーセクションの終わりを検出
                if line.startswith('AutoAnalysis.Marker.Data.StartCondition,'):
                    self.auto_analysis_start = i

                # データセクションの開始行を検出
                if ',' in line and not self.columns and self.auto_analysis_start > 0 and i > self.auto_analysis_start:
                    potential_columns = [col.strip() for col in line.split(',')]
                    # データセクションの開始行は列名の行
                    if len(potential_columns) > 1:
                        self.columns = potential_columns
                        self.data_section_start = i
                        break

                # ヘッダー情報を抽出
                if ',' in line and self.auto_analysis_start < 0:
                    parts = line.split(',', 1)
                    if len(parts) == 2:
                        key, value = parts
                        self.header_info[key.strip()] = value.strip()

            if self.data_section_start < 0:
                raise ValueError("Could not find data section in file")

            self.logger.info("Header parsed successfully")

        except Exception as e:
            self.logger.error("Error parsing header: %s", str(e))
            raise

    def _extract_data(self) -> None:
        """
        データセクションからデータを抽出する
        - 列名の行の次の行からが実際のデータ
        """
        try:
            # データ行を抽出
            data_lines = []
            for line in self.raw_data[self.data_section_start + 1:]:
                line = line.strip()
                if line and ',' in line:
                    values = line.split(',')
                    values = [np.nan if v == '' else v for v in values]
                    data_lines.append(values)

            # データフレームを作成
            self.df = pd.DataFrame(data_lines, columns=self.columns)

            # 数値データの列を数値型に変換
            for col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

            self.logger.info("Data extracted successfully: %d rows, %d columns",
                             len(self.df), len(self.columns))

        except Exception as e:
            self.logger.error("Error extracting data: %s", str(e))
            raise

    def get_device_info(self) -> Dict:
        """デバイス情報を取得する"""
        device_info = {
            'device_id': self.header_info.get('Device ID', ''),
            'test_date': self.header_info.get('Test date', ''),
            'test_time': self.header_info.get('Test time', ''),
            'setup_title': self.header_info.get('Setup title', ''),
            'test_name': self.header_info.get('Classic test name', '')
        }
        return device_info

    def save_parsed_data(self, output_path: Optional[str] = None) -> str:
        """
        解析したデータをCSV形式で保存する

        Args:
            output_path: 保存先のパス。Noneの場合は元のファイル名に_parsedを付加

        Returns:
            str: 保存したファイルのパス
        """
        if self.df is None:
            raise ValueError("No data to save. Please load data first.")

        if output_path is None:
            original_path = Path(self.input_file)
            output_path = str(original_path.parent / f"{original_path.stem}_parsed.csv")

        self.save_cleaned_data(output_path)
        return output_path

    def process(self, cleaning_config: Optional[dict] = None) -> pd.DataFrame:
        """
        データの前処理

        Args:
            cleaning_config: 前処理設定

        Returns:
            pd.DataFrame: 前処理後のデータフレーム
        """
        try:
            self.load_data()

            if cleaning_config:
                # 親クラスのprocess処理を呼び出し
                super().process(cleaning_config)

            self.logger.info("B1500 data processing completed successfully")
            return self.df

        except Exception as e:
            self.logger.error("Error processing B1500 data: %s", str(e))
            raise

    def validate_data(self, validation_rules=None):
        pass


if __name__ == "__main__":
    input_file = "data/sample_data.csv"
    output_file = "data/cleaned_data.csv"
    cleaning_config = {
        'missing_values': 'drop',
        'data_types': {
            'age': 'int',
            'salary': 'float64'
        },
        'validation_rules': {
            'age': {
                'min': 0,
                'max': 100
            },
            'salary': {
                'min': 0,
            }
        }
    }
    # default example
    loader = DefaultDataLoader(input_file=input_file, device_name="cpu")
    cleaned_data = loader.process(cleaning_config)
    loader.save_cleaned_data(output_file)

    # B1500A example
    loader = Sample2DataLoader(input_file="data/sample_data.csv", device_name="b1500a")
    loader.load_data()
    print(loader.ret_data())
