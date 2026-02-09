Az func app code:
import os
import json
import logging

import azure.functions as func
from sqlalchemy import create_engine, text

HARDCODED_DATABASE_URL = "postgresql+psycopg2://{connectionStringhere}}/postgres"

engine = create_engine(HARDCODED_DATABASE_URL, pool_pre_ping=True)
logging.info(f"Attempting to connect to: postgresql")
# -----------------------
# Function App
# -----------------------
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
 
@app.route(route="esg_escalation", methods=["POST"])
def esg_escalation(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("azure_function_triggered for escalation insert data")

    try:
        # Parse JSON body sent from Power Automate
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON body"}),
                status_code=400,
                mimetype="application/json"
            )

        # Extract values from the request body
        escid = req_body.get("escid")
        vendorid = req_body.get("vendorid")
        datajson = req_body.get("datajson")  # can be dict or string
        created_at = req_body.get("created_at")  # optional
        updated_at = req_body.get("updated_at")  # optional
        esc_type = req_body.get("esc_type")  # optional
        supplier_name = req_body.get("supplier_name")
        esc_reason=req_body.get("esc_reason")
        comments=req_body.get("comments")  # optional

        # Convert dict to string if necessary
        if isinstance(datajson, dict):
            datajson = json.dumps(datajson)

        # Validate required fields
        if not escid or not vendorid:
            return func.HttpResponse(
                json.dumps({"error": "Missing required fields: escid or vendorid"}),
                status_code=400,
                mimetype="application/json"
            )

        #  Corrected SQL (column order matches values)
        insert_sql = text("""
            INSERT INTO esclation_request (
                escid, 
                vendorid, 
                datajson, 
                created_at, 
                updated_at, 
                esc_type, 
                supplier_name,
                esc_reason,
                comments
            )
            VALUES (
                :escid, 
                :vendorid, 
                :datajson, 
                COALESCE(:created_at, NOW()), 
                COALESCE(:updated_at, NOW()), 
                :esc_type, 
                :supplier_name,
                :esc_reason,
                :comments
            )
            RETURNING *;
        """)

        # Execute the SQL
        with engine.begin() as conn:
            result = conn.execute(insert_sql, {
                "escid": escid,
                "vendorid": vendorid,
                "datajson": datajson,
                "created_at": created_at,
                "updated_at": updated_at,
                "esc_type": esc_type,
                "supplier_name": supplier_name,
                "esc_reason": esc_reason,
                "comments": comments
            })
            row_obj = result.fetchone()

        row = dict(row_obj._mapping) if row_obj else None
        logging.info(f"Inserted escalation record: {row}")

        return func.HttpResponse(
            json.dumps({
                "message": "Insert successful in escalation_request table",
                "item": row
            }, default=str),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.exception("Error while inserting record into escalation_request")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="esg_escalation_approval", methods=["POST"])
def esg_escalation_approval(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Azure Function triggered for escalation_approval operation record")

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON body"}),
            status_code=400,
            mimetype="application/json"
        )

    try:
        operation = req_body.get("operation")
        if not operation:
            return func.HttpResponse(
                json.dumps({"error": "operation field is required (Create/Update)"}),
                status_code=400,
                mimetype="application/json"
            )

        # ============ CREATE OPERATION ============
        if operation.lower() == "create":
            escid = req_body.get("escid")
            responder_name = req_body.get("responder_name")
            approval_id = req_body.get("approval_id")
            escalation_request_status = req_body.get("escalation_request_status")
            vendor_code = req_body.get("vendor_code")
            created_at = req_body.get("created_at")
            updated_at = req_body.get("updated_at")
            esc_type=req_body.get("esc_type")  # optional

            if not escid:
                return func.HttpResponse(
                    json.dumps({"error": "escid is required for insert"}),
                    status_code=400,
                    mimetype="application/json"
                )

            insert_sql = text("""
                INSERT INTO esclation_approval (escid, responder_name, approval_id, escalation_request_status, vendor_code, created_at, updated_at, esc_type)
                VALUES (:escid, :responder_name, :approval_id, :escalation_request_status, :vendor_code,COALESCE(:created_at, NOW()), COALESCE(:updated_at, NOW()), :esc_type)
                RETURNING *;
            """)

            with engine.begin() as conn:
                result = conn.execute(insert_sql, {
                    "escid": escid,
                    "responder_name": responder_name,
                    "approval_id": approval_id,
                    "escalation_request_status": escalation_request_status,
                    "vendor_code": vendor_code,
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "esc_type": esc_type
                })
                row_obj = result.fetchone()

            row = dict(row_obj._mapping) if row_obj else None
            logging.info(f"Inserted esclation_approval record: {row}")

            return func.HttpResponse(
                json.dumps({"message": "Insert successful (esclation_approval)", "item": row}, default=str),
                status_code=200,
                mimetype="application/json"
            )

        # ============ UPDATE OPERATION ============
        elif operation.lower() == "update":
            escid = req_body.get("escid")
            approval_status = req_body.get("approval_status")
            comments = req_body.get("comments")
            escalation_request_status = req_body.get("escalation_request_status")
            approval_id = req_body.get("approval_id")

            if not escid:
                return func.HttpResponse(
                    json.dumps({"error": "escid is required to update record"}),
                    status_code=400,
                    mimetype="application/json"
                )

            update_sql = text("""
                UPDATE esclation_approval
                SET approval_status = :approval_status,
                    comments = :comments,
                    escalation_request_status = :escalation_request_status,
                    updated_at = NOW()
                WHERE escid = :escid
                  AND approval_id = :approval_id
                RETURNING *;
            """)

            with engine.begin() as conn:
                result = conn.execute(update_sql, {
                    "escid": escid,
                    "approval_status": approval_status,
                    "comments": comments,
                    "escalation_request_status": escalation_request_status,
                    "approval_id": approval_id
                    
                })
                row_obj = result.fetchone()

            if not row_obj:
                return func.HttpResponse(
                    json.dumps({"error": f"No record found for escid {escid}"}),
                    status_code=404,
                    mimetype="application/json"
                )

            row = dict(row_obj._mapping)
            logging.info(f"Updated esclation_approval record: {row}")

            return func.HttpResponse(
                json.dumps({"message": "Update successful (esclation_approval)", "item": row}, default=str),
                status_code=200,
                mimetype="application/json"
            )
        elif operation.lower() == "updatefinalstatus":
            escid = req_body.get("escid")
            escalation_request_status = req_body.get("escalation_request_status")
            approval_id1 = req_body.get("approval_id1")
            approval_id2 = req_body.get("approval_id2")

            if not escid or not approval_id1 or not approval_id2:
                return func.HttpResponse(
                    json.dumps({"error": "Both escid and approval_ids list are required to update records"}),
                    status_code=400,
                    mimetype="application/json"
                )
            
            
            
            update_sql=text("""
                UPDATE esclation_approval
                SET escalation_request_status = :escalation_request_status,
                    updated_at = NOW()
                WHERE escid = :escid
                  AND approval_id IN (:approval_id1, :approval_id2)
                RETURNING *;
            """)


            with engine.begin() as conn:
                result = conn.execute(update_sql, {
                    "escid": escid,
                    "escalation_request_status": escalation_request_status,
                    "approval_id1": approval_id1,
                    "approval_id2": approval_id2
                })
                rows = result.fetchall()

            if not rows:
                return func.HttpResponse(
                    json.dumps({"error": f"No records found for escid {escid} and approval_ids approval_ids"}),
                    status_code=404,
                    mimetype="application/json"
                )
            
            row_list=[dict(row._mapping) for row in rows]
            logging.info(f"Updated esclation_approval records: {row_list}")

            return func.HttpResponse(
                json.dumps({"message": "UpdateFinalStatus successful for multiple records (esclation_approval)", "items": row_list}, default=str),
                status_code=200,
                mimetype="application/json"
            )


        # ============ INVALID OPERATION ============
        else:
            return func.HttpResponse(
                json.dumps({"error": f"Unsupported operation: {operation}. Use 'Create' or 'Update'."}),
                status_code=400,
                mimetype="application/json"
            )

    except Exception as e:
        logging.exception("Error in esclation_approval operation")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
