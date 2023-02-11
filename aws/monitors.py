import enum
import time
from datetime import datetime, timedelta
from logging import Logger
from typing import Any, Callable, TypedDict

from django.conf import settings


class Unit(enum.Enum):
    SECONDS = "Seconds"
    MICROSECONDS = "Microseconds"
    MILLISECONDS = "Milliseconds"

    COUNT = "Count"
    PERCENT = "Percent"

    BYTES = "Bytes"


class Metrics(enum.Enum):
    CPU_UTILIZATION = "CPUUtilization", Unit.PERCENT.value
    CPU_CREDIT_BALANCE = "CPUCreditBalance", Unit.COUNT.value
    CPU_CREDIT_USAGE = "CPUCreditUsage", Unit.PERCENT.value
    # CPU_SURPLUS_CREDIT_BALANCE = 'CPUSurplusCreditBalance',

    BURST_BALANCE = "BurstBalance", Unit.PERCENT.value

    BIN_LOG_DISK_USAGE = "BinLogDiskUsage", Unit.BYTES.value


class Statistics(enum.Enum):
    SAMPLE_COUNT = "SampleCount"
    AVERAGE = "Average"
    SUM = "Sum"
    MINIMUM = "Minimum"
    MAXIMUM = "Maximum"


class DatapointDict(TypedDict):
    timestamp: datetime
    value: Any
    unit: str


class BaseMetricsMonitor:
    service: str
    dimension_name: str
    dimension_value: str

    class OverAttemptError(Exception):
        pass

    def __init__(
        self,
        metrics: Metrics,
        statistic: Statistics = Statistics.AVERAGE.value,
        logger: Logger | None = None,
    ):
        import boto3

        self.metric_name, self.unit = metrics
        self.statistic = statistic
        self.logger = logger
        self.client = boto3.client("cloudwatch", **self.get_client_kwargs())

    def wait_until(
        self,
        run_if: Callable,
        attempt_time: int = 10,
        wait_seconds: int = 60,
        delta: timedelta = timedelta(seconds=60 * 30),
        period: int = 60,
    ):
        now = datetime.utcnow()
        for i in range(attempt_time):
            dp = self.get_datapoints(now - delta, now, period=period)[0]
            self.log(f"データポイントを確認 ... {dp}")
            if run_if(dp["value"]):
                break

            self.log(f'{dp["value"]} は基準に達しませんでした')
            self.log(f"待機中 ... {i + 1} 回目")
            time.sleep(wait_seconds)
            self.log("待機終了")
        else:
            raise self.OverAttemptError("メトリクスが基準に達しなかったため、処理を中断しました")

    def _get_datapoints(
        self, start_time: datetime, end_time: datetime, period: int = 300
    ) -> list[dict]:
        response = self.client.get_metric_statistics(
            Namespace=f"AWS/{self.service}",
            Dimensions=[{"Name": self.dimension_name, "Value": self.dimension_value}],
            MetricName=self.metric_name,
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Unit=self.unit,
            Statistics=[self.statistic],
        )

        return sorted(
            response["Datapoints"], key=lambda point: point["Timestamp"], reverse=True
        )

    def get_datapoints(
        self,
        start_time: datetime,
        end_time: datetime,
        period: int = 300,
        row: bool = False,
    ):
        datapoints = self._get_datapoints(start_time, end_time, period)
        if row:
            return datapoints

        datapoints = [
            {
                "timestamp": p["Timestamp"],
                "value": p[self.statistic],  # 指定した Statistic ('Average') として渡される
                "unit": p["Unit"],
            }
            for p in datapoints
        ]

        return datapoints

    def log(self, msg: str):
        if self.logger:
            self.logger.info(msg)
        else:
            print(msg)

    def get_client_kwargs(self) -> dict:
        return {
            "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": settings.AWS_ACCESS_KEY,
            "region_name": settings.AWS_REGION,
        }
