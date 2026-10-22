import asyncio
import io
import json
import os
import pandas as pd
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
from app.vi_cluster import base as vi_base
import logging
from app.core.logging_stream import QueueLogHandler
from app.core.config import USERS, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from typing import Optional
import zipfile
import uuid
import time
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt  # PyJWT import
from pydantic import BaseModel

app = FastAPI()
logger = logging.getLogger("consensus")

# Directory to store generated output files temporarily
OUTPUT_DIR = "generated_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_pipeline_zip(cluster_df, consensus_df, df_purity_scores) -> str:
    """
    Zips multiple dataframes, logs, or text files together.
    Returns the file path of the created zip archive.
    """
    job_id = uuid.uuid4().hex[:10]
    zip_filename = f"consensus_results_{job_id}.zip"
    zip_filepath = os.path.join(OUTPUT_DIR, zip_filename)

    with zipfile.ZipFile(
        zip_filepath, "w", compression=zipfile.ZIP_DEFLATED
    ) as zip_file:
        # 1. Add Cluster Metrics CSV from DataFrame
        cluster_csv = cluster_df.to_csv(index=False)
        zip_file.writestr("cluster_metrics.csv", cluster_csv)

        # 2. Add Consensus Sequences CSV from DataFrame
        consensus_csv = consensus_df.to_csv(index=False)
        zip_file.writestr("consensus_sequences.csv", consensus_csv)

        df_purity_csv = df_purity_scores.to_csv(index=False)
        zip_file.writestr("df_purity_scores.csv", df_purity_csv)

        # 3. Add Pipeline Log File
        # zip_file.writestr("execution_log.txt", log_text)

        # 4. (Optional) Add existing disk files, e.g., a README or summary figure
        # zip_file.write(filename="/path/to/summary.png", arcname="summary_plot.png")

    return zip_filename


def cleanup_file(file_path: str):
    """Deletes the file from disk if it exists."""
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Failed to delete temp file {file_path}: {e}")


def format_metadata_filters(metadata_filters):
    filters = {}
    for filt in metadata_filters:
        if filt.get("notNullOnly", False):
            filters[filt.get("column")] = {"not_null": True}
        else:
            filters[filt.get("column")] = filt.get("values")
    return filters


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")


class Token(BaseModel):
    access_token: str
    token_type: str


def verify_password(plain_password, stored_password):
    return plain_password == stored_password


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})

    # PyJWT encode (returns a string directly in PyJWT v2+)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # PyJWT decode (validates expiration and signature automatically)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except (
        jwt.PyJWTError
    ):  # Catches expired tokens, invalid signatures, malformed strings, etc.
        raise credentials_exception

    if username not in USERS:
        raise credentials_exception
    return username


@app.post("/api/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = USERS.get(form_data.username)
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/consensus")
async def run_consensus_analysis(
    metadata_file: UploadFile = File(...),
    counts_file: UploadFile = File(...),
    genotype_file: UploadFile = File(...),
    threshold: float = Form(0.85),
    clustering_method: str = Form("ward"),
    min_cluster_size: int = Form(3),
    crop_name: str = Form("Wheat"),
    pca_marker_percentage: float = Form(90.0),
    metadata_filters: Optional[str] = Form(None),
):
    current_user: str = Depends(get_current_user)
    log_queue = asyncio.Queue()

    async def event_generator():
        # 1. Attach the custom log handler for this specific request
        handler = QueueLogHandler(log_queue)
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        handler.setFormatter(formatter)

        # Attach to root or specific module logger so internal logging statements are captured
        target_logger = logging.getLogger()
        target_logger.addHandler(handler)
        target_logger.setLevel(logging.INFO)

        async def analysis_task():
            try:
                target_logger.info("Reading uploaded files asynchronously...")
                target_logger.info(f"Metadata Filter: {metadata_filters}")
                filters = format_metadata_filters(json.loads(metadata_filters))
                target_logger.info(f"Formatted Metadata Filter: {filters}")
                target_logger.info(f"pca_perc: {pca_marker_percentage}")
                contents_metadata = await metadata_file.read()
                contents_counts = await counts_file.read()
                contents_genotype = await genotype_file.read()
                pca_markers_to_keep = pca_marker_percentage / 100
                target_logger.info(
                    f"Starting consensus generation for {crop_name} (min_cluster_size={min_cluster_size})..."
                )

                # 2. Run your synchronous bioinformatics pipeline in a background thread
                graph_payload, result_df, consensus_df, df_purity_scores = (
                    await asyncio.to_thread(
                        vi_base.generate_consensus_sequences,
                        metadata_file=io.BytesIO(contents_metadata),
                        counts_file=io.BytesIO(contents_counts),
                        genotype_file=io.BytesIO(contents_genotype),
                        minimum_sample_size=min_cluster_size,
                        pca_marker_percentage=pca_markers_to_keep,
                        metaFilter=filters,
                    )
                )

                target_logger.info(
                    "Clustering and consensus analysis completed. Formatting output files..."
                )

                # 3. Save the output file for download
                output_filename = "consensus_analysis_result.csv"
                output_path = os.path.join(OUTPUT_DIR, output_filename)

                # result_df = pd.DataFrame(
                #     {
                #         "Sample_ID": ["S01", "S02", "S03"],
                #         "Consensus_Score": [0.92, 0.88, 0.95],
                #         "Cluster": [1, 2, 1],
                #     }
                # )

                zip_filename = create_pipeline_zip(
                    result_df, consensus_df, df_purity_scores
                )

                result_df.to_csv(output_path, index=False)

                target_logger.info("Pipeline execution successfully finished.")

                return {
                    "status": "success",
                    "graphs": graph_payload,
                    "download_url": f"/api/download/{zip_filename}",
                    "parameters_used": {
                        "threshold": threshold,
                        "clustering_method": clustering_method,
                        "min_cluster_size": min_cluster_size,
                        "crop_name": crop_name,
                    },
                }

            except Exception as e:
                target_logger.error(f"Analysis failed: {str(e)}")
                raise e
            finally:
                # Clean up handler so logs don't persist across requests
                target_logger.removeHandler(handler)

        # 5. Kick off the analysis task concurrently
        task = asyncio.create_task(analysis_task())

        # 6. Stream logs from the queue as they happen
        while not task.done() or not log_queue.empty():
            try:
                log_msg = await asyncio.wait_for(log_queue.get(), timeout=0.1)
                yield json.dumps({"type": "log", "message": log_msg}) + "\n"
            except asyncio.TimeoutError:
                continue

        # 7. Yield the final result packet once the task finishes successfully
        try:
            result = await task  # Now correctly evaluates to a Python dictionary
            yield json.dumps(
                {
                    "type": "result",
                    "status": result["status"],
                    "graphs": result["graphs"],
                    "download_url": result["download_url"],
                    "parameters_used": result["parameters_used"],
                }
            ) + "\n"
        except Exception:
            yield json.dumps({"type": "result", "status": "failure"}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")


# Endpoint to handle downloading the generated output file
# @app.get("/api/download/{filename}")
# async def download_file(filename: str):
#     file_path = os.path.join(OUTPUT_DIR, filename)
#     if os.path.exists(file_path):
#         return FileResponse(
#             file_path, media_type="application/octet-stream", filename=filename
#         )
#     raise HTTPException(status_code=404, detail="File not found")


@app.get("/api/download/{filename}")
async def download_zip(filename: str, background_tasks: BackgroundTasks):
    file_path = os.path.join(OUTPUT_DIR, filename)

    if not os.path.exists(file_path):
        return {"error": "File not found or already expired"}

    # Schedule the deletion task to run *after* the file streams to the user
    background_tasks.add_task(cleanup_file, file_path)

    return FileResponse(path=file_path, media_type="application/zip", filename=filename)


@app.on_event("startup")
async def cleanup_old_output_files():
    """Purges any leftover zip files older than 2 hours upon server startup."""
    if not os.path.exists(OUTPUT_DIR):
        return

    now = time.time()
    two_hours_in_seconds = 2 * 60 * 60

    for filename in os.listdir(OUTPUT_DIR):
        if filename.endswith(".zip"):
            file_path = os.path.join(OUTPUT_DIR, filename)
            # Check file age
            if os.path.isfile(file_path) and (
                now - os.path.getmtime(file_path) > two_hours_in_seconds
            ):
                try:
                    os.remove(file_path)
                except Exception:
                    pass
