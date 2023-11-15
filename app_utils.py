template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Query Result</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .content {
          margin-bottom: 20px;}
        .content p { font-size: 16px; }
        .images-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
        }
        .images-grid img {
            flex: 1 0 21%; /* Adjusts to roughly 5 images per row at full size */
            max-width: 100%;
            height: auto;
            border-radius: 4px; /* Optional: just for styled corners */
            object-fit: cover;
        }
        .references {
            margin-top: 20px;
        }
        .references h2 {
            margin-bottom: 10px;
        }
        .references ul {
            list-style-type: none;
            padding: 0;
        }
        .references li a {
            text-decoration: none;
            color: #0645AD;
        }
        .references li a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="content">
        <h2>Content</h2>
        <p>{{ content }}</p>
    </div>
    {% if images %}
    <div class="images">
        <h2>Images Results</h2>
        <div class="images-grid">
            {% for image in images %}
            <img src="{{ image }}" alt="Image">
            {% endfor %}
        </div>
    </div>
    {% endif %}
    {% if references %}
    <div class="references">
        <h2>References</h2>
        <ul>
            {% for reference in references %}
            <li><a href="{{ reference }}" target="_blank">{{ reference }}</a></li>
            {% endfor %}
        </ul>
    </div>
    {% endif %}
</body>
</html>

"""
desc = '''
<p>Explore the cutting-edge capabilities of our intelligent open-source agent, powered by the Zephyr-7B-beta model. This interactive demo showcases our system's proficiency in processing and analyzing factual information across the web, utilizing advanced techniques like Retriever-Augmented Generation, keyword extraction, and intelligent web page segmentation. Experience firsthand how our tool delivers personalized, accurate, and efficient assistance in real-time.</p>
'''
