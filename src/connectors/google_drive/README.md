# Google Drive Connector — Technical Documentation

> **Platform:** Node Wire
> **Connector ID:** `google_drive`
> **Endpoint:** `POST /connectors/google_drive/execute`
> **Discriminator:** `action` field (discriminated-union payload)
> **Source:** `connectors/google_drive/`

---

## 1. Operations Overview

All requests go through a single `execute` endpoint. The `action` field determines which Google Drive operation runs. All responses share a common output shape and error taxonomy enforced by the runtime.

### Available Operations

| Action | Description |
|---|---|
| `files.list` | List or search files with optional query and fields mask |
| `files.create` | Create file metadata (no content) or create inside a folder |
| `permissions.create` | Grant a user access to a file (reader, commenter, writer, owner) |
| `files.get` | Fetch metadata for a specific file |
| `files.update` | Update file metadata and parent relationships |
| `files.upload` | Create a new file with text content |
| `files.delete` | Delete a file |

### Planned Operations

The following operations are planned for future implementation:

- **`files.generateIds`** — Pre-generate IDs to avoid duplicate uploads during retries.
- **`changes.watch`** — Trigger workflows the moment a file is uploaded.
- **`revisions.list`** — Allows users to see who changed what and when.
- **`files.export`** — Export Google Docs, Sheets, or Slides to `.docx`, `.pdf`, or `.csv` (no traditional download; export required).

---

## 2. Operation Reference

### `files.list`

List or search files visible to the service account. The connector always sends a `fields` mask to the Drive API; if omitted, a performant default is used so only commonly needed metadata is returned.

| Field | Type | Required | Description |
|---|---|---|---|
| `action` | string | ✅ | Must be `"files.list"` |
| `page_size` | int | No | Default `10`, range `1–100`. Maximum files to return |
| `query` | string | No | Drive search query (`q` parameter) |
| `fields` | string | No | Fields mask. Default: `"nextPageToken, files(id, name, mimeType, webViewLink)"` |

**Request body — minimal (default fields):**

```json
{
  "action": "files.list",
  "page_size": 10
}
```

**Request body — with query and custom fields:**

```json
{
  "action": "files.list",
  "page_size": 20,
  "query": "mimeType = 'application/pdf'",
  "fields": "nextPageToken, files(id, name, mimeType, webViewLink, modifiedTime)"
}
```

**Typical success response:**

```json
{
  "success": true,
  "data": {
    "raw": {
      "files": [
        { "id": "1...", "name": "example.txt", "mimeType": "text/plain" }
      ]
    },
    "description": "Successfully executed files.list"
  },
  "error_code": null,
  "error_category": null,
  "message": null,
  "trace_id": "..."
}
```

---

### `files.create`

Create a new file metadata entry (no content) or create inside a folder. The service account must have write access to the parent folder.

| Field | Type | Required | Description |
|---|---|---|---|
| `action` | string | ✅ | Must be `"files.create"` |
| `name` | string | ✅ | File name |
| `mime_type` | string | No | Drive MIME type |
| `parents` | array of string | No | Parent folder IDs |

```json
{
  "action": "files.create",
  "name": "example.txt",
  "mime_type": "text/plain",
  "parents": ["<FOLDER_ID>"]
}
```

---

### `permissions.create`

Grant a user access to a file. The service account must have permission to change sharing on the file.

| Field | Type | Required | Description |
|---|---|---|---|
| `action` | string | ✅ | Must be `"permissions.create"` |
| `file_id` | string | ✅ | ID of the target file |
| `role` | string | ✅ | `"reader"`, `"commenter"`, `"writer"`, or `"owner"` |
| `email_address` | string | ✅ | Email address to grant access to |

```json
{
  "action": "permissions.create",
  "file_id": "<FILE_ID>",
  "role": "reader",
  "email_address": "user@example.com"
}
```

---

### `files.get`

Fetch metadata for a specific file.

| Field | Type | Required | Description |
|---|---|---|---|
| `action` | string | ✅ | Must be `"files.get"` |
| `file_id` | string | ✅ | ID of the target file |
| `fields` | string | No | Fields mask passed to Drive. Default: `"id,name,mimeType,parents"` |

```json
{
  "action": "files.get",
  "file_id": "<FILE_ID>",
  "fields": "id,name,mimeType,parents"
}
```

---

### `files.update`

Update file metadata and parent relationships. The service account must have edit permission on the file.

| Field | Type | Required | Description |
|---|---|---|---|
| `action` | string | ✅ | Must be `"files.update"` |
| `file_id` | string | ✅ | ID of the file to update |
| `name` | string | No | New file name |
| `mime_type` | string | No | New MIME type |
| `add_parents` | array of string | No | Folder IDs to add (mapped to `addParents`) |
| `remove_parents` | array of string | No | Folder IDs to remove (mapped to `removeParents`) |

```json
{
  "action": "files.update",
  "file_id": "<FILE_ID>",
  "name": "renamed.txt",
  "mime_type": "text/plain",
  "add_parents": ["<NEW_FOLDER_ID>"],
  "remove_parents": ["<OLD_FOLDER_ID>"]
}
```

---

### `files.upload`

Create a new file with text content. Content is uploaded using `MediaInMemoryUpload`; suitable for small text payloads.

| Field | Type | Required | Description |
|---|---|---|---|
| `action` | string | ✅ | Must be `"files.upload"` |
| `name` | string | ✅ | File name |
| `mime_type` | string | ✅ | MIME type |
| `parents` | array of string | No | Parent folder IDs |
| `content` | string | ✅ | UTF-8 text content to upload |

```json
{
  "action": "files.upload",
  "name": "hello.txt",
  "mime_type": "text/plain",
  "parents": ["<FOLDER_ID>"],
  "content": "Hello from Node Wire connector!"
}
```

---

### `files.delete`

Delete a file. The service account must have permission to delete the file.

| Field | Type | Required | Description |
|---|---|---|---|
| `action` | string | ✅ | Must be `"files.delete"` |
| `file_id` | string | ✅ | ID of the file to delete |

```json
{
  "action": "files.delete",
  "file_id": "<FILE_ID>"
}
```

On success, the connector returns a synthetic confirmation payload:

```json
{
  "success": true,
  "data": {
    "raw": {
      "file_id": "<FILE_ID>",
      "status": "deleted"
    },
    "description": "Successfully executed files.delete"
  },
  "error_code": null,
  "error_category": null,
  "message": null,
  "trace_id": "..."
}
```

---

## 3. Error Taxonomy

All Google Drive errors are mapped into the platform error taxonomy using wrapper exceptions. The connector never raises raw `HttpError` — it always translates errors into one of these exception classes so the platform can apply consistent retry and circuit-breaker behaviour.

| Error Code | Category | Trigger Conditions |
|---|---|---|
| `GDRIVE_AUTH` | `AUTH` | Authentication/authorisation issues (401, 403 without rate-limit reason) |
| `GDRIVE_RATE_LIMIT` | `RETRYABLE` | Quota or rate limit issues (403 `quotaExceeded`/`rateLimitExceeded`, 429, 5xx) |
| `GDRIVE_BUSINESS_RULE` | `BUSINESS` | Invalid IDs, conflicts, not found (400, 404, 409) |
| `GDRIVE_FATAL` | `FATAL` | Any unhandled `HttpError` status or unexpected exception |

### HTTP Status Code Mapping

| Category | HTTP Status |
|---|---|
| `BUSINESS` | `400` |
| `AUTH` | `401` |
| `RETRYABLE` | `503` |
| `FATAL` | `500` |
