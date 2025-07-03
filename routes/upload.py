from flask import Blueprint, request, render_template, redirect, url_for, flash
from services.chroma_service import load_business_knowledge
from database.models import db, Business
import os

upload_bp = Blueprint("upload", __name__)

@upload_bp.route("/upload_knowledge/<int:business_id>", methods=["GET", "POST"])
def upload_knowledge(business_id):
    business = db.session.query(Business).filter_by(id=business_id).first()

    if request.method == "POST":
        raw_text = request.form.get("knowledge", "").strip()

        if business:
            business.system_prompt = raw_text
            db.session.commit()

            # טען ל־Chroma
            num_chunks = load_business_knowledge(business_id, raw_text)
            print(f"{num_chunks} קטעים נטענו ל־Chroma לעסק {business_id}")

            flash("✔️ המידע נשמר בהצלחה!", "success")
        else:
            flash("⚠️ לא נמצא עסק עם המזהה הזה.", "error")

        return redirect(url_for("upload.upload_knowledge", business_id=business_id))

    existing_prompt = business.system_prompt if business else ""
    return render_template("upload_knowledge.html", business_id=business_id, existing_prompt=existing_prompt)
