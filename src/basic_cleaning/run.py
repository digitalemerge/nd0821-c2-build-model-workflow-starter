#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact.
"""
import argparse
import logging
import wandb
import os
import pathlib
import pandas as pd
from typing import *

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def import_data(pth: Union[str, pathlib.Path]) -> pd.DataFrame:
    """
    returns dataframe for the csv found at pth

    input:
            pth: a path to the csv
    output:
            data_frame: pandas dataframe
    """
    dataframe = pd.read_csv(pth)
    return dataframe


def drop_outliers_price(data_frame: pd.DataFrame) -> pd.DataFrame:
    """
    Drop outliers for the price column in the given dataframe.

    input:
            data_frame: Dataframe with column Price.
    output:
            data_frame: pandas dataframe without outliers in the Price column
    """
    min_price = float(args.min_price)
    max_price = float(args.max_price)

    dataframe_index = data_frame['price'].between(min_price, max_price)
    data_frame=data_frame[dataframe_index]

    return data_frame

def drop_outliers_price(data_frame: pd.DataFrame) -> pd.DataFrame:
    """
    Drop outliers for the lat and lon columns in the given dataframe.

    input:
            data_frame: Dataframe with columns lat & lon.
    output:
            data_frame: pandas dataframe without outliers in the lat & lon columns.
    """

    data_frame_index = data_frame['longitude'].between(-74.25, -73.50) & data_frame['latitude'].between(40.5, 41.2)
    data_frame = data_frame[data_frame_index].copy()

def column_2_datetime(data_frame: pd.DataFrame, col_name: str) -> pd.DataFrame:
    """
    Transforms objects of the column 'last_review' to datetime object. Any other frame
    with an arbitrary colomn with datetime-like objects can be given.

    input:
            data_frame: Dataframe with column 'last_review'.
            col_name: String specifying the column name.
    output:
            data_frame: pandas dataframe with datetime objects to be transformed to datetime.
    """
    data_frame[col_name] = pd.to_datetime(data_frame[col_name])

    return data_frame


def frame_2_csv(data_frame: pd.DataFrame, output: Union[str, pathlib.Path]) -> None:
    """
        Write data_frame to csv in local disk.

        input:
                data_frame: Dataframe with cleansed columns.
                _output: Output to write the dataframe to.
        output:
                None
        """
    data_frame.to_csv(output, index=False)


def add_log_wandb_artifact(artifact_output: Any, artifact_type: str, artifact_description: str, run: wandb.run) -> None:
    """
            Creates an artifact instance, adds and the artifact in the input arguments and logs the artifact with
            the artifact type in the input.

            input:
                    artifact: Artifact to add and log
                    type:     Type of the artifact given.
            output:
                    None
            """
    artifact = wandb.Artifact(
        str(artifact_output),
        type=artifact_type,
        description=artifact_description,
    )
    artifact.add_file(artifact_output)
    run.log_artifact(artifact)


def remove_local_output(args: Dict[Any, Any]) -> None:
    """
                Removes temporary local csv files.

                input:
                        args:       Dictionary of arguments as input

                output:
                        None
                """
    os.remove(args.output_artifact)


def go(args: Dict[Any, Any]) -> None:

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()

    logger.info(f"Fetching data artifact {args.input_artifact} from wandb.")
    artifact_local_path = run.use_artifact(args.input_artifact).file()
    logger.info("Data artifact fetched successfully.")

    data_frame = import_data(artifact_local_path)
    data_frame = drop_outliers_price(data_frame)
    data_frame = column_2_datetime(data_frame, 'last_review')
    data_frame = drop_outliers_lat_lon(data_frame)
    frame_2_csv(data_frame, args.output_artifact)
    add_log_wandb_artifact("clean_sample.csv", args.output_type, args.output_description, run)
    remove_local_output(args)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")

    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Wandb argument to be passed as input.",
        required=True
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="Wandb output argument to be produced after the basic cleaning steps.",
        required=True
    )

    parser.add_argument(
        "--output_type",
        type=str,
        help="Wandb argument type produced by the output of this step.",
        required=True
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help="Description of the artifact created after this cleaning step.",
        required=True
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help="Lower threshold for the price column in the data.",
        required=True
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="Upper threshold for the price column in the data.",
        required=True
    )

    args = parser.parse_args()

    go(args)
