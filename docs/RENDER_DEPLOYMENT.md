# Deployment Guide (Render + Hugging Face)

Because the Python AI Service is resource-intensive (parsing resumes, running NLP models), deploying everything as a single monolith on Render's free tier can lead to out-of-memory errors. 

To resolve this, the architecture has been split:
1. **Frontend (React) & Backend (Node.js)** run together on **Render** (via Docker).
2. **AI Service (Python)** runs on **Hugging Face Spaces** (via Docker).
3. **Database** runs on **MongoDB Atlas**.

## 1. Setting Up MongoDB (Atlas)

1. Create a free cluster on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
2. Create a database user and password.
3. In Network Access, whitelist `0.0.0.0/0` (Allow access from anywhere).
4. Copy your connection string (e.g., `mongodb+srv://<username>:<password>@cluster0.mongodb.net/srrss?retryWrites=true&w=majority`).

## 2. Deploying the AI Service (Hugging Face Spaces)

Hugging Face provides free Docker Spaces which are perfect for our AI Service.

1. Create an account on [Hugging Face](https://huggingface.co/).
2. Go to your profile and click **New Space**.
3. Fill in the details:
   - **Space Name**: e.g., `srrss-ai-service`
   - **License**: Choose MIT or your preference.
   - **Select the Space SDK**: Choose **Docker** -> **Blank**.
   - **Space Hardware**: Free tier is sufficient.
4. Click **Create Space**.
5. Once created, you will see instructions to clone the Space repository.
6. Copy the contents of the `ai-service/` folder (including the new `Dockerfile` and `requirements.txt`) directly into the root of your new Hugging Face Space repository. You can do this via Git or the Hugging Face web interface (Add File -> Upload files).
7. Go to the **Settings** tab of your Space -> **Variables and secrets** -> **Secrets**.
   - Add a new secret:
     - Name: `AI_SERVICE_API_KEY`
     - Value: Generate a random secure string (e.g., `super_secret_ai_key_123`). Save this, as you'll need it for Render!
8. Hugging Face will automatically build the Dockerfile and start the FastAPI service.
9. Your AI Service URL will be something like: `https://<your-username>-srrss-ai-service.hf.space`. Copy this URL.

## 3. Deploying the Backend & Frontend (Render)

1. Go to your [Render Dashboard](https://dashboard.render.com).
2. Click **New** -> **Web Service**.
3. Connect your repository.
4. Choose **Docker** as the Runtime.
5. Provide a name (e.g., `srrss-web`).
6. Leave the rest of the settings to default (Render automatically detects the `Dockerfile` at the root of the repo, which we've updated to ONLY run the Node.js app).
7. Scroll down to **Environment Variables** and add the following:

### Required Variables:
- `MONGODB_URI`: Your MongoDB Atlas connection string.
- `MONGODB_TLS`: `true`
- `CLIENT_URL`: The public URL(s) allowed to call the backend. Use a comma-separated list with no extra quotes, for example `https://srrss.codes,https://www.srrss.codes,https://srrss-z5yz.onrender.com`.
- `FRONTEND_URL`: Optional fallback list for the same allowed origins. If you set it, use the same comma-separated format and no quotes.
- `AI_SERVICE_URL`: The Hugging Face Space URL you copied earlier (e.g., `https://<your-username>-srrss-ai-service.hf.space`).
- `AI_SERVICE_API_KEY`: The EXACT same secret key you added to Hugging Face.

### R2 Storage Variables (Required for file uploads):
- `R2_ACCOUNT_ID`: Your Cloudflare account ID.
- `R2_ACCESS_KEY_ID`: Cloudflare R2 access key.
- `R2_SECRET_ACCESS_KEY`: Cloudflare R2 secret key.
- `R2_BUCKET_NAME`: `srrss` (or your bucket name).

### Authentication Secrets:
- `JWT_SECRET`: A secure random string.
- `JWT_REFRESH_SECRET`: Another secure random string.

8. Click **Create Web Service**.

## 4. What to Test After Deploy

Once the service is live:

1. **Frontend**: Open the Render app URL. It should load the UI.
2. **Backend API**: Check `<your-render-url>/api/health`. It should return a 200 OK.
3. **Internal AI Connection**: Try uploading or parsing a resume. The backend should successfully proxy requests to your Hugging Face Space.
4. **Client-Side Routing**: Refresh the page on a nested route (e.g., `/dashboard`) to confirm that the backend correctly serves `index.html`.

## 5. Common Gotchas

- **App crashes on startup**: Check if your `MONGODB_URI` is correct and if `0.0.0.0/0` is whitelisted in Atlas.
- **AI processing fails**: Make sure `AI_SERVICE_URL` and `AI_SERVICE_API_KEY` exactly match your Hugging Face deployment.
- **Files not uploading**: Verify your Cloudflare R2 credentials.
- **CORS blocks frontend assets**: Make sure the Render public URL is included in `CLIENT_URL` or `FRONTEND_URL`, and do not wrap the values in quotes.
