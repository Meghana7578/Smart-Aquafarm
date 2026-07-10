from flask import Flask, render_template, request
from db import connection, cursor
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from flask import send_file
from openpyxl import Workbook
import os

app = Flask(__name__)

# ==========================
# HOME PAGE
# ==========================
@app.route("/")
def home():
    return render_template("index.html")


# ==========================
# REGISTER PAGE
# ==========================
@app.route("/register")
def register():
    return render_template("register.html")


# ==========================
# SAVE USER
# ==========================
@app.route("/saveuser", methods=["POST"])
def saveuser():

    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]

    sql = """
    INSERT INTO USERS1
    (
        ID,
        NAME,
        EMAIL,
        PASSWORD
    )
    VALUES
    (
        USERS1_SEQ.NEXTVAL,
        :1,
        :2,
        :3
    )
    """

    try:

        cursor.execute(sql, (name, email, password))
        connection.commit()

        return """
        <script>
            alert("Registration Successful");
            window.location="/login";
        </script>
        """

    except Exception as e:

        return f"""
        <h2>Database Error</h2>
        <p>{e}</p>
        """


# ==========================
# LOGIN PAGE
# ==========================
@app.route("/login")
def login():

    return render_template("login.html")


# ==========================
# LOGIN VALIDATION
# ==========================
@app.route("/loginuser", methods=["POST"])
def loginuser():

    email = request.form["email"]
    password = request.form["password"]

    sql = """
    SELECT *
    FROM USERS1
    WHERE EMAIL=:1
    AND PASSWORD=:2
    """

    try:

        cursor.execute(sql, (email, password))

        user = cursor.fetchone()

        if user:

            return render_template("dashboard.html")

        else:

            return """
            <script>
                alert("Invalid Email or Password");
                window.location="/login";
            </script>
            """

    except Exception as e:

        return f"""
        <h2>Login Error</h2>
        <p>{e}</p>
        """


# ==========================
# LOGOUT
# ==========================
@app.route("/logout")
def logout():

    return """
    <script>
        alert("Logged Out Successfully");
        window.location="/";
    </script>
    """
@app.route("/addpond")
def addpond():

    return render_template("add_pond.html")

@app.route("/savepond", methods=["POST"])
def savepond():

    pond_name = request.form["pond_name"]
    species = request.form["species"]
    area = request.form["area"]
    fish_count = request.form["fish_count"]

    sql = """
    INSERT INTO PONDS
    (
        POND_ID,
        POND_NAME,
        SPECIES,
        AREA,
        FISH_COUNT
    )

    VALUES
    (
        PONDS_SEQ.NEXTVAL,
        :1,
        :2,
        :3,
        :4
    )
    """

    cursor.execute(sql,
    (
        pond_name,
        species,
        area,
        fish_count
    ))

    connection.commit()

    return """
    <script>

    alert("Pond Added Successfully");

    window.location="/dashboard";

    </script>

    """
@app.route("/dashboard")
def dashboard():

    # Total Ponds
    cursor.execute("""
        SELECT COUNT(*)
        FROM PONDS
    """)

    total_ponds = cursor.fetchone()[0]



    # Total Fish

    cursor.execute("""
        SELECT NVL(SUM(FISH_COUNT),0)
        FROM PONDS
    """)

    total_fish = cursor.fetchone()[0]



    # Latest Pond

    cursor.execute("""
        SELECT POND_NAME
        FROM PONDS
        WHERE POND_ID =
        (
            SELECT MAX(POND_ID)
            FROM PONDS
        )
    """)

    row = cursor.fetchone()

    if row:

        latest_pond = row[0]

    else:

        latest_pond = "No Pond"



    return render_template(

        "dashboard.html",

        total_ponds=total_ponds,

        total_fish=total_fish,

        latest_pond=latest_pond

    )
@app.route("/ponds")
def ponds():

    sql = """
    SELECT
        POND_ID,
        POND_NAME,
        SPECIES,
        AREA,
        FISH_COUNT
    FROM PONDS
    ORDER BY POND_ID
    """

    cursor.execute(sql)

    pond_list = cursor.fetchall()

    return render_template(
        "ponds.html",
        ponds=pond_list
    )
# ==========================
# EDIT POND PAGE
# ==========================
@app.route("/editpond/<int:pond_id>")
def editpond(pond_id):

    sql = """
    SELECT
        POND_ID,
        POND_NAME,
        SPECIES,
        AREA,
        FISH_COUNT
    FROM PONDS
    WHERE POND_ID = :1
    """

    cursor.execute(sql, (pond_id,))

    pond = cursor.fetchone()

    return render_template(
        "edit_pond.html",
        pond=pond
    )
# ==========================
# UPDATE POND
# ==========================
@app.route("/updatepond", methods=["POST"])
def updatepond():

    pond_id = request.form["pond_id"]
    pond_name = request.form["pond_name"]
    species = request.form["species"]
    area = request.form["area"]
    fish_count = request.form["fish_count"]

    sql = """
    UPDATE PONDS
    SET
        POND_NAME = :1,
        SPECIES = :2,
        AREA = :3,
        FISH_COUNT = :4
    WHERE
        POND_ID = :5
    """

    cursor.execute(sql,
    (
        pond_name,
        species,
        area,
        fish_count,
        pond_id
    ))

    connection.commit()

    return """
    <script>

        alert("Pond Updated Successfully");

        window.location="/ponds";

    </script>
    """
# ==========================
# DELETE POND
# ==========================
@app.route("/deletepond/<int:pond_id>")
def deletepond(pond_id):

    sql = """
    DELETE FROM PONDS
    WHERE POND_ID = :1
    """

    cursor.execute(sql, (pond_id,))

    connection.commit()

    return """
    <script>

        alert("Pond Deleted Successfully");

        window.location="/ponds";

    </script>
    """
# ==========================
# FISH GROWTH PAGE
# ==========================
@app.route("/growth")
def growth():

    cursor.execute("""
        SELECT
            POND_ID,
            POND_NAME
        FROM PONDS
        ORDER BY POND_NAME
    """)

    ponds = cursor.fetchall()

    return render_template(
        "growth.html",
        ponds=ponds
    )
# ==========================
# SAVE FISH GROWTH
# ==========================
@app.route("/savegrowth", methods=["POST"])
def savegrowth():

    pond_id = request.form["pond_id"]
    growth_date = request.form["growth_date"]
    avg_weight = request.form["avg_weight"]
    avg_length = request.form["avg_length"]
    fish_count = request.form["fish_count"]

    sql = """
    INSERT INTO FISH_GROWTH
    (
        GROWTH_ID,
        POND_ID,
        GROWTH_DATE,
        AVG_WEIGHT,
        AVG_LENGTH,
        FISH_COUNT
    )
    VALUES
    (
        FISH_GROWTH_SEQ.NEXTVAL,
        :1,
        TO_DATE(:2,'YYYY-MM-DD'),
        :3,
        :4,
        :5
    )
    """

    cursor.execute(sql,
    (
        pond_id,
        growth_date,
        avg_weight,
        avg_length,
        fish_count
    ))

    connection.commit()

    return """
    <script>

        alert("Fish Growth Saved Successfully");

        window.location="/growth";

    </script>
    """
# ==========================
# VIEW GROWTH RECORDS
# ==========================
@app.route("/growthrecords")
def growthrecords():

    cursor.execute("""
    SELECT
        G.GROWTH_ID,
        P.POND_NAME,
        G.GROWTH_DATE,
        G.AVG_WEIGHT,
        G.AVG_LENGTH,
        G.FISH_COUNT
    FROM FISH_GROWTH G
    JOIN PONDS P
    ON G.POND_ID=P.POND_ID
    ORDER BY G.GROWTH_ID DESC
    """)

    records = cursor.fetchall()

    # Total Records
    cursor.execute("""
    SELECT COUNT(*)
    FROM FISH_GROWTH
    """)

    total_records = cursor.fetchone()[0]

    # Average Weight
    cursor.execute("""
    SELECT NVL(ROUND(AVG(AVG_WEIGHT),2),0)
    FROM FISH_GROWTH
    """)

    average_weight = cursor.fetchone()[0]

    # Average Length
    cursor.execute("""
    SELECT NVL(ROUND(AVG(AVG_LENGTH),2),0)
    FROM FISH_GROWTH
    """)

    average_length = cursor.fetchone()[0]

    return render_template(
        "growth_records.html",
        growth=records,
        total_records=total_records,
        average_weight=average_weight,
        average_length=average_length
    )
# ==========================
# UPDATE GROWTH
# ==========================
@app.route("/updategrowth", methods=["POST"])
def updategrowth():

    growth_id = request.form["growth_id"]
    growth_date = request.form["growth_date"]
    avg_weight = request.form["avg_weight"]
    avg_length = request.form["avg_length"]
    fish_count = request.form["fish_count"]

    sql = """
    UPDATE FISH_GROWTH
    SET
        GROWTH_DATE = TO_DATE(:1,'YYYY-MM-DD'),
        AVG_WEIGHT = :2,
        AVG_LENGTH = :3,
        FISH_COUNT = :4
    WHERE
        GROWTH_ID = :5
    """

    cursor.execute(sql,
    (
        growth_date,
        avg_weight,
        avg_length,
        fish_count,
        growth_id
    ))

    connection.commit()

    return """
    <script>

    alert("Growth Record Updated Successfully");

    window.location="/growthrecords";

    </script>
    """
# ==========================
# DELETE GROWTH
# ==========================
@app.route("/deletegrowth/<int:growth_id>")
def deletegrowth(growth_id):

    sql = """
    DELETE FROM FISH_GROWTH
    WHERE GROWTH_ID = :1
    """

    cursor.execute(sql, (growth_id,))

    connection.commit()

    return """
    <script>

    alert("Growth Record Deleted Successfully");

    window.location="/growthrecords";

    </script>
    """
# ==========================
# FEEDING RECORDS
# ==========================
@app.route("/feedingrecords")
def feedingrecords():

    sql = """
    SELECT

        F.FEED_ID,

        P.POND_NAME,

        F.FEED_DATE,

        F.FEED_TYPE,

        F.QUANTITY,

        F.FEED_TIME

    FROM

        FEEDING F

    JOIN

        PONDS P

    ON

        F.POND_ID = P.POND_ID

    ORDER BY

        F.FEED_ID DESC
    """

    cursor.execute(sql)

    feeding = cursor.fetchall()


    # Total Records

    cursor.execute("""
    SELECT COUNT(*)
    FROM FEEDING
    """)

    total_records = cursor.fetchone()[0]


    # Total Quantity

    cursor.execute("""
    SELECT NVL(SUM(QUANTITY),0)
    FROM FEEDING
    """)

    total_quantity = cursor.fetchone()[0]


    return render_template(

        "feeding_records.html",

        feeding=feeding,

        total_records=total_records,

        total_quantity=total_quantity

    )
# ==========================
# ADD FEEDING PAGE
# ==========================
@app.route("/feeding")
def feeding():

    cursor.execute("""
    SELECT

        POND_ID,

        POND_NAME

    FROM PONDS

    ORDER BY POND_NAME
    """)

    ponds = cursor.fetchall()

    return render_template(

        "feeding.html",

        ponds=ponds

    )
# ==========================
# SAVE FEEDING
# ==========================
@app.route("/savefeeding", methods=["POST"])
def savefeeding():

    pond_id = request.form["pond_id"]
    feed_date = request.form["feed_date"]
    feed_type = request.form["feed_type"]
    quantity = request.form["quantity"]
    feed_time = request.form["feed_time"]

    sql = """
    INSERT INTO FEEDING
    (

        FEED_ID,

        POND_ID,

        FEED_DATE,

        FEED_TYPE,

        QUANTITY,

        FEED_TIME

    )

    VALUES
    (

        FEEDING_SEQ.NEXTVAL,

        :1,

        TO_DATE(:2,'YYYY-MM-DD'),

        :3,

        :4,

        :5

    )
    """

    cursor.execute(

        sql,

        (

            pond_id,

            feed_date,

            feed_type,

            quantity,

            feed_time

        )

    )

    connection.commit()

    return """
    <script>

    alert("Feeding Record Saved Successfully");

    window.location="/feedingrecords";

    </script>
    """
# ==========================
# EDIT FEEDING PAGE
# ==========================
@app.route("/editfeeding/<int:feed_id>")
def editfeeding(feed_id):

    sql = """
    SELECT
        FEED_ID,
        POND_ID,
        TO_CHAR(FEED_DATE,'YYYY-MM-DD'),
        FEED_TYPE,
        QUANTITY,
        FEED_TIME
    FROM FEEDING
    WHERE FEED_ID=:1
    """

    cursor.execute(sql, (feed_id,))

    record = cursor.fetchone()

    return render_template(
        "edit_feeding.html",
        record=record
    )
# ==========================
# UPDATE FEEDING
# ==========================
@app.route("/updatefeeding", methods=["POST"])
def updatefeeding():

    feed_id = request.form["feed_id"]
    feed_date = request.form["feed_date"]
    feed_type = request.form["feed_type"]
    quantity = request.form["quantity"]
    feed_time = request.form["feed_time"]

    sql = """
    UPDATE FEEDING
    SET
        FEED_DATE=TO_DATE(:1,'YYYY-MM-DD'),
        FEED_TYPE=:2,
        QUANTITY=:3,
        FEED_TIME=:4
    WHERE
        FEED_ID=:5
    """

    cursor.execute(
        sql,
        (
            feed_date,
            feed_type,
            quantity,
            feed_time,
            feed_id
        )
    )

    connection.commit()

    return """
    <script>

    alert("Feeding Record Updated Successfully");

    window.location="/feedingrecords";

    </script>
    """
# ==========================
# DELETE FEEDING
# ==========================
@app.route("/deletefeeding/<int:feed_id>")
def deletefeeding(feed_id):

    sql = """
    DELETE FROM FEEDING
    WHERE FEED_ID=:1
    """

    cursor.execute(sql, (feed_id,))

    connection.commit()

    return """
    <script>

    alert("Feeding Record Deleted Successfully");

    window.location="/feedingrecords";

    </script>
    """
# ==========================
# WATER QUALITY RECORDS
# ==========================
@app.route("/waterqualityrecords")
def waterqualityrecords():

    sql = """
    SELECT

        W.QUALITY_ID,

        P.POND_NAME,

        W.CHECK_DATE,

        W.PH_LEVEL,

        W.TEMPERATURE,

        W.DISSOLVED_OXYGEN,

        W.AMMONIA

    FROM WATER_QUALITY W

    JOIN PONDS P

    ON W.POND_ID = P.POND_ID

    ORDER BY W.QUALITY_ID DESC
    """

    cursor.execute(sql)

    water = cursor.fetchall()


    # Total Records

    cursor.execute("""

    SELECT COUNT(*)

    FROM WATER_QUALITY

    """)

    total_records = cursor.fetchone()[0]


    # Average pH

    cursor.execute("""

    SELECT NVL(ROUND(AVG(PH_LEVEL),2),0)

    FROM WATER_QUALITY

    """)

    avg_ph = cursor.fetchone()[0]


    return render_template(

        "water_quality_records.html",

        water=water,

        total_records=total_records,

        avg_ph=avg_ph

    )


# ==========================
# ADD WATER QUALITY PAGE
# ==========================
@app.route("/waterquality")
def waterquality():

    cursor.execute("""

    SELECT

        POND_ID,

        POND_NAME

    FROM PONDS

    ORDER BY POND_NAME

    """)

    ponds = cursor.fetchall()

    return render_template(

        "water_quality.html",

        ponds=ponds

    )


# ==========================
# SAVE WATER QUALITY
# ==========================
@app.route("/savewaterquality", methods=["POST"])
def savewaterquality():

    pond_id = request.form["pond_id"]

    check_date = request.form["check_date"]

    ph_level = request.form["ph_level"]

    temperature = request.form["temperature"]

    dissolved_oxygen = request.form["dissolved_oxygen"]

    ammonia = request.form["ammonia"]


    sql = """

    INSERT INTO WATER_QUALITY

    (

        QUALITY_ID,

        POND_ID,

        CHECK_DATE,

        PH_LEVEL,

        TEMPERATURE,

        DISSOLVED_OXYGEN,

        AMMONIA

    )

    VALUES

    (

        WATER_QUALITY_SEQ.NEXTVAL,

        :1,

        TO_DATE(:2,'YYYY-MM-DD'),

        :3,

        :4,

        :5,

        :6

    )

    """


    cursor.execute(

        sql,

        (

            pond_id,

            check_date,

            ph_level,

            temperature,

            dissolved_oxygen,

            ammonia

        )

    )


    connection.commit()


    return """

    <script>

    alert("Water Quality Record Saved Successfully");

    window.location="/waterqualityrecords";

    </script>

    """
# ==========================
# EDIT WATER QUALITY PAGE
# ==========================
@app.route("/editwaterquality/<int:quality_id>")
def editwaterquality(quality_id):

    sql = """
    SELECT
        QUALITY_ID,
        POND_ID,
        TO_CHAR(CHECK_DATE,'YYYY-MM-DD'),
        PH_LEVEL,
        TEMPERATURE,
        DISSOLVED_OXYGEN,
        AMMONIA
    FROM WATER_QUALITY
    WHERE QUALITY_ID = :1
    """

    cursor.execute(sql, (quality_id,))

    record = cursor.fetchone()

    return render_template(
        "edit_water_quality.html",
        record=record
    )
# ==========================
# UPDATE WATER QUALITY
# ==========================
@app.route("/updatewaterquality", methods=["POST"])
def updatewaterquality():

    quality_id = request.form["quality_id"]
    check_date = request.form["check_date"]
    ph_level = request.form["ph_level"]
    temperature = request.form["temperature"]
    dissolved_oxygen = request.form["dissolved_oxygen"]
    ammonia = request.form["ammonia"]

    sql = """
    UPDATE WATER_QUALITY
    SET
        CHECK_DATE = TO_DATE(:1,'YYYY-MM-DD'),
        PH_LEVEL = :2,
        TEMPERATURE = :3,
        DISSOLVED_OXYGEN = :4,
        AMMONIA = :5
    WHERE
        QUALITY_ID = :6
    """

    cursor.execute(
        sql,
        (
            check_date,
            ph_level,
            temperature,
            dissolved_oxygen,
            ammonia,
            quality_id
        )
    )

    connection.commit()

    return """
    <script>

    alert("Water Quality Record Updated Successfully");

    window.location="/waterqualityrecords";

    </script>
    """
# ==========================
# DELETE WATER QUALITY
# ==========================
@app.route("/deletewaterquality/<int:quality_id>")
def deletewaterquality(quality_id):

    sql = """
    DELETE FROM WATER_QUALITY
    WHERE QUALITY_ID = :1
    """

    cursor.execute(sql, (quality_id,))

    connection.commit()

    return """
    <script>

    alert("Water Quality Record Deleted Successfully");

    window.location="/waterqualityrecords";

    </script>
    """
# ==========================
# DISEASE RECORDS
# ==========================
@app.route("/diseaserecords")
def diseaserecords():

    sql = """
    SELECT

        D.DISEASE_ID,

        P.POND_NAME,

        D.DISEASE_NAME,

        D.DETECTION_DATE,

        D.TREATMENT,

        D.STATUS

    FROM DISEASES D

    JOIN PONDS P

    ON D.POND_ID = P.POND_ID

    ORDER BY D.DISEASE_ID DESC
    """

    cursor.execute(sql)

    diseases = cursor.fetchall()

    # Total Records

    cursor.execute("""

    SELECT COUNT(*)

    FROM DISEASES

    """)

    total_records = cursor.fetchone()[0]

    # Recovered Fish

    cursor.execute("""

    SELECT COUNT(*)

    FROM DISEASES

    WHERE STATUS='Recovered'

    """)

    recovered = cursor.fetchone()[0]

    return render_template(

        "disease_records.html",

        diseases=diseases,

        total_records=total_records,

        recovered=recovered

    )


# ==========================
# ADD DISEASE PAGE
# ==========================
@app.route("/disease")
def disease():

    cursor.execute("""

    SELECT

        POND_ID,

        POND_NAME

    FROM PONDS

    ORDER BY POND_NAME

    """)

    ponds = cursor.fetchall()

    return render_template(

        "disease.html",

        ponds=ponds

    )


# ==========================
# SAVE DISEASE
# ==========================
@app.route("/savedisease", methods=["POST"])
def savedisease():

    pond_id = request.form["pond_id"]

    disease_name = request.form["disease_name"]

    detection_date = request.form["detection_date"]

    treatment = request.form["treatment"]

    status = request.form["status"]

    sql = """

    INSERT INTO DISEASES

    (

        DISEASE_ID,

        POND_ID,

        DISEASE_NAME,

        DETECTION_DATE,

        TREATMENT,

        STATUS

    )

    VALUES

    (

        DISEASES_SEQ.NEXTVAL,

        :1,

        :2,

        TO_DATE(:3,'YYYY-MM-DD'),

        :4,

        :5

    )

    """

    cursor.execute(

        sql,

        (

            pond_id,

            disease_name,

            detection_date,

            treatment,

            status

        )

    )

    connection.commit()

    return """

    <script>

    alert("Disease Record Saved Successfully");

    window.location="/diseaserecords";

    </script>

    """
# ==========================
# EDIT DISEASE PAGE
# ==========================
@app.route("/editdisease/<int:disease_id>")
def editdisease(disease_id):

    sql = """
    SELECT
        DISEASE_ID,
        POND_ID,
        DISEASE_NAME,
        TO_CHAR(DETECTION_DATE,'YYYY-MM-DD'),
        TREATMENT,
        STATUS
    FROM DISEASES
    WHERE DISEASE_ID=:1
    """

    cursor.execute(sql, (disease_id,))

    record = cursor.fetchone()

    return render_template(
        "edit_disease.html",
        record=record
    )
# ==========================
# UPDATE DISEASE
# ==========================
@app.route("/updatedisease", methods=["POST"])
def updatedisease():

    disease_id = request.form["disease_id"]
    disease_name = request.form["disease_name"]
    detection_date = request.form["detection_date"]
    treatment = request.form["treatment"]
    status = request.form["status"]

    sql = """
    UPDATE DISEASES
    SET
        DISEASE_NAME=:1,
        DETECTION_DATE=TO_DATE(:2,'YYYY-MM-DD'),
        TREATMENT=:3,
        STATUS=:4
    WHERE
        DISEASE_ID=:5
    """

    cursor.execute(
        sql,
        (
            disease_name,
            detection_date,
            treatment,
            status,
            disease_id
        )
    )

    connection.commit()

    return """
    <script>

    alert("Disease Record Updated Successfully");

    window.location="/diseaserecords";

    </script>
    """
# ==========================
# DELETE DISEASE
# ==========================
@app.route("/deletedisease/<int:disease_id>")
def deletedisease(disease_id):

    sql = """
    DELETE FROM DISEASES
    WHERE DISEASE_ID=:1
    """

    cursor.execute(sql, (disease_id,))

    connection.commit()

    return """
    <script>

    alert("Disease Record Deleted Successfully");

    window.location="/diseaserecords";

    </script>
    """
# ==========================
# MARKET PRICE RECORDS
# ==========================
@app.route("/marketrecords")
def marketrecords():

    sql = """
    SELECT

        PRICE_ID,

        FISH_SPECIES,

        MARKET_NAME,

        PRICE_PER_KG,

        PRICE_DATE

    FROM MARKET_PRICES

    ORDER BY PRICE_DATE DESC
    """

    cursor.execute(sql)

    market = cursor.fetchall()

    # Total Records

    cursor.execute("""

    SELECT COUNT(*)

    FROM MARKET_PRICES

    """)

    total_records = cursor.fetchone()[0]

    # Average Price

    cursor.execute("""

    SELECT NVL(ROUND(AVG(PRICE_PER_KG),2),0)

    FROM MARKET_PRICES

    """)

    average_price = cursor.fetchone()[0]

    return render_template(

        "market_records.html",

        market=market,

        total_records=total_records,

        average_price=average_price

    )


# ==========================
# ADD MARKET PRICE PAGE
# ==========================
@app.route("/market")
def market():

    return render_template("market.html")


# ==========================
# SAVE MARKET PRICE
# ==========================
@app.route("/savemarket", methods=["POST"])
def savemarket():

    fish_species = request.form["fish_species"]

    market_name = request.form["market_name"]

    price_per_kg = request.form["price_per_kg"]

    price_date = request.form["price_date"]

    sql = """

    INSERT INTO MARKET_PRICES

    (

        PRICE_ID,

        FISH_SPECIES,

        MARKET_NAME,

        PRICE_PER_KG,

        PRICE_DATE

    )

    VALUES

    (

        MARKET_PRICES_SEQ.NEXTVAL,

        :1,

        :2,

        :3,

        TO_DATE(:4,'YYYY-MM-DD')

    )

    """

    cursor.execute(

        sql,

        (

            fish_species,

            market_name,

            price_per_kg,

            price_date

        )

    )

    connection.commit()

    return """

    <script>

    alert("Market Price Saved Successfully");

    window.location="/marketrecords";

    </script>

    """
# ==========================
# EDIT MARKET PRICE
# ==========================
@app.route("/editmarket/<int:price_id>")
def editmarket(price_id):

    sql = """
    SELECT
        PRICE_ID,
        FISH_SPECIES,
        MARKET_NAME,
        PRICE_PER_KG,
        TO_CHAR(PRICE_DATE,'YYYY-MM-DD')
    FROM MARKET_PRICES
    WHERE PRICE_ID=:1
    """

    cursor.execute(sql, (price_id,))

    record = cursor.fetchone()

    return render_template(
        "edit_market.html",
        record=record
    )
# ==========================
# UPDATE MARKET PRICE
# ==========================
@app.route("/updatemarket", methods=["POST"])
def updatemarket():

    price_id = request.form["price_id"]
    fish_species = request.form["fish_species"]
    market_name = request.form["market_name"]
    price_per_kg = request.form["price_per_kg"]
    price_date = request.form["price_date"]

    sql = """
    UPDATE MARKET_PRICES
    SET
        FISH_SPECIES=:1,
        MARKET_NAME=:2,
        PRICE_PER_KG=:3,
        PRICE_DATE=TO_DATE(:4,'YYYY-MM-DD')
    WHERE
        PRICE_ID=:5
    """

    cursor.execute(
        sql,
        (
            fish_species,
            market_name,
            price_per_kg,
            price_date,
            price_id
        )
    )

    connection.commit()

    return """
    <script>

    alert("Market Price Updated Successfully");

    window.location="/marketrecords";

    </script>
    """
# ==========================
# DELETE MARKET PRICE
# ==========================
@app.route("/deletemarket/<int:price_id>")
def deletemarket(price_id):

    sql = """
    DELETE FROM MARKET_PRICES
    WHERE PRICE_ID=:1
    """

    cursor.execute(sql, (price_id,))

    connection.commit()

    return """
    <script>

    alert("Market Price Deleted Successfully");

    window.location="/marketrecords";

    </script>
    """
    # ==========================
# REPORTS DASHBOARD
# ==========================
@app.route("/reports")
def reports():

    # Total Ponds
    cursor.execute("SELECT COUNT(*) FROM PONDS")
    total_ponds = cursor.fetchone()[0]

    # Total Fish
    cursor.execute("""
    SELECT NVL(SUM(FISH_COUNT),0)
    FROM PONDS
    """)
    total_fish = cursor.fetchone()[0]

    # Growth Records
    cursor.execute("""
    SELECT COUNT(*)
    FROM FISH_GROWTH
    """)
    growth_records = cursor.fetchone()[0]

    # Feeding Records
    cursor.execute("""
    SELECT COUNT(*)
    FROM FEEDING
    """)
    feeding_records = cursor.fetchone()[0]

    # Water Records
    cursor.execute("""
    SELECT COUNT(*)
    FROM WATER_QUALITY
    """)
    water_records = cursor.fetchone()[0]

    # Disease Records
    cursor.execute("""
    SELECT COUNT(*)
    FROM DISEASES
    """)
    disease_records = cursor.fetchone()[0]

    # Market Records
    cursor.execute("""
    SELECT COUNT(*)
    FROM MARKET_PRICES
    """)
    market_records = cursor.fetchone()[0]

    return render_template(
        "reports.html",
        total_ponds=total_ponds,
        total_fish=total_fish,
        growth_records=growth_records,
        feeding_records=feeding_records,
        water_records=water_records,
        disease_records=disease_records,
        market_records=market_records
    )
# ==========================
# DOWNLOAD PDF REPORT
# ==========================
@app.route("/downloadpdf")
def downloadpdf():

    pdf_file = "Smart_AquaFarm_Report.pdf"

    document = SimpleDocTemplate(pdf_file)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(

        Paragraph(

            "<b>Smart AquaFarm Report</b>",

            styles["Title"]

        )

    )

    elements.append(

        Paragraph(

            "Farm Summary",

            styles["Heading2"]

        )

    )

    cursor.execute("SELECT COUNT(*) FROM PONDS")
    total_ponds = cursor.fetchone()[0]

    cursor.execute("SELECT NVL(SUM(FISH_COUNT),0) FROM PONDS")
    total_fish = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM FISH_GROWTH")
    growth = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM FEEDING")
    feeding = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM WATER_QUALITY")
    water = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM DISEASES")
    disease = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM MARKET_PRICES")
    market = cursor.fetchone()[0]

    data = [

        ["Module", "Total"],

        ["Ponds", total_ponds],

        ["Fish", total_fish],

        ["Growth Records", growth],

        ["Feeding Records", feeding],

        ["Water Records", water],

        ["Disease Records", disease],

        ["Market Prices", market]

    ]

    table = Table(data)

    table.setStyle(

        TableStyle([

            ("BACKGROUND",(0,0),(-1,0),colors.green),

            ("TEXTCOLOR",(0,0),(-1,0),colors.white),

            ("GRID",(0,0),(-1,-1),1,colors.black),

            ("BACKGROUND",(0,1),(-1,-1),colors.beige),

            ("ALIGN",(0,0),(-1,-1),"CENTER"),

            ("BOTTOMPADDING",(0,0),(-1,0),10)

        ])

    )

    elements.append(table)

    document.build(elements)

    return send_file(

        pdf_file,

        as_attachment=True

    )
# ==========================
# DOWNLOAD EXCEL REPORT
# ==========================
@app.route("/downloadexcel")
def downloadexcel():

    workbook = Workbook()

    sheet = workbook.active

    sheet.title = "Smart AquaFarm Report"

    # Heading
    sheet.append(["Module", "Total Records"])

    # Fetch Data
    cursor.execute("SELECT COUNT(*) FROM PONDS")
    total_ponds = cursor.fetchone()[0]

    cursor.execute("SELECT NVL(SUM(FISH_COUNT),0) FROM PONDS")
    total_fish = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM FISH_GROWTH")
    growth = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM FEEDING")
    feeding = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM WATER_QUALITY")
    water = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM DISEASES")
    disease = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM MARKET_PRICES")
    market = cursor.fetchone()[0]

    # Add Data
    sheet.append(["Total Ponds", total_ponds])
    sheet.append(["Total Fish", total_fish])
    sheet.append(["Growth Records", growth])
    sheet.append(["Feeding Records", feeding])
    sheet.append(["Water Quality Records", water])
    sheet.append(["Disease Records", disease])
    sheet.append(["Market Price Records", market])

    file_name = "Smart_AquaFarm_Report.xlsx"

    workbook.save(file_name)

    return send_file(
        file_name,
        as_attachment=True
    )

# ==========================
# MAIN
# ==========================
if __name__ == "__main__":
    app.run(debug=True)