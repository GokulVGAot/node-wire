from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Patient – Read (single patient by ID or name search)
# ---------------------------------------------------------------------------

class FhirPatientReadInput(BaseModel):
    """Input for reading a single FHIR Patient resource from Epic."""

    resource_id: Optional[str] = None
    """Direct Patient ID lookup (e.g. 'eXYZ123')."""

    # Convenience name fields — take priority over raw search_params when set.
    given_name: Optional[str] = None
    """Patient given / first name (used in name-based search)."""

    family_name: Optional[str] = None
    """Patient family / last name (used in name-based search)."""

    name: Optional[str] = None
    """Full or partial name string — mapped to FHIR 'name' search parameter.

    Use this when you only have a single combined name string.  When both
    ``name`` and ``given_name``/``family_name`` are set, the explicit given/
    family fields take precedence.
    """

    birthdate: Optional[str] = None
    """Date of birth in YYYY-MM-DD format — used alongside name search."""

    search_params: Optional[Dict[str, str]] = None
    """Raw FHIR search parameters (e.g. {\"family\": \"Smith\", \"given\": \"John\"}).

    Lowest priority — used only when no ID or explicit name fields are set.
    """


class FhirPatientReadOutput(BaseModel):
    """Output for reading a FHIR Patient resource."""

    resource: Dict[str, Any]
    """The raw FHIR Patient JSON object."""


# ---------------------------------------------------------------------------
# Patient – Search (multi-ID fan-out OR name search returning multiple results)
# ---------------------------------------------------------------------------

class FhirPatientSearchInput(BaseModel):
    """Input for searching / fetching multiple FHIR Patient resources from Epic.

    Two modes are supported:

    1. **Multi-ID lookup** — pass ``resource_ids`` (list of Patient IDs).
       Each ID is fetched concurrently; partial failures are captured in
       ``FhirPatientSearchOutput.errors`` rather than raising globally.

    2. **Name-based search** — pass ``given_name``, ``family_name``, ``name``,
       and/or ``birthdate``.  A single FHIR search request is issued and all
       matching Bundle entries are returned.

    Only one mode should be used per request.  If ``resource_ids`` is set it
    takes priority over the name/search fields.
    """

    resource_ids: Optional[List[str]] = None
    """List of Epic Patient IDs to fetch concurrently (e.g. ['eABC', 'eDEF'])."""

    given_name: Optional[str] = None
    """Patient given / first name."""

    family_name: Optional[str] = None
    """Patient family / last name."""

    name: Optional[str] = None
    """Full or partial name string — mapped to FHIR 'name' search parameter."""

    birthdate: Optional[str] = None
    """Date of birth in YYYY-MM-DD format."""

    search_params: Optional[Dict[str, str]] = None
    """Additional raw FHIR search parameters merged with the name fields."""


class FhirPatientSearchOutput(BaseModel):
    """Output for searching multiple FHIR Patient resources."""

    resources: List[Dict[str, Any]]
    """List of successfully retrieved FHIR Patient JSON objects."""

    total: Optional[int] = None
    """Total number of matches reported by the server Bundle (name-search mode)."""

    errors: List[Dict[str, Any]] = []
    """Per-ID errors encountered during multi-ID fan-out.

    Each entry has the shape::

        {"resource_id": "<id>", "error": "<message>"}

    An empty list means all lookups succeeded.
    """


# ---------------------------------------------------------------------------
# Encounter – Search
# ---------------------------------------------------------------------------

class FhirEncounterSearchInput(BaseModel):
    """Input for searching FHIR Encounter resources."""

    patient_id: Optional[str] = None
    """FHIR Patient ID to find encounters for (maps to 'patient' FHIR param)."""

    status: Optional[str] = None
    """Status of the encounters to find (e.g. 'finished', 'arrived')."""

    date: Optional[str] = None
    """Date or date range for the encounters (e.g. '2024', 'gt2023-01-01')."""

    search_params: Optional[Dict[str, str]] = None
    """Raw FHIR search parameters. Used if explicit fields above are not provided."""


class FhirEncounterSearchOutput(BaseModel):
    """Output for searching FHIR Encounter resources."""

    resources: list[Dict[str, Any]]
    """The list of raw FHIR Encounter JSON objects found."""

    total: Optional[int] = None
    """Total number of results reported by the Bundle."""


# ---------------------------------------------------------------------------
# DocumentReference – Create
# ---------------------------------------------------------------------------

class FhirDocumentReferenceCreateInput(BaseModel):
    """Input for creating a FHIR DocumentReference resource."""

    identifier: list[Dict[str, Any]]
    """Document identifier."""

    status: str
    """The document status (usually 'current')."""

    type: Dict[str, Any]
    """Document type (CodeableConcept)."""

    category: Optional[list[Dict[str, Any]]] = None
    """Category (CodeableConcept). Epic does not require this field."""

    subject: str
    """Patient reference string (e.g. 'Patient/{id}'). Required by Epic."""

    data: str
    """Base64-encoded document content. Required by Epic."""

    content_type: Optional[str] = None
    """MIME type of the document content (e.g. 'text/plain', 'application/pdf'). Defaults to 'text/plain'."""

    author: Optional[list[Dict[str, Any]]] = None
    """Author of the document (e.g. Practitioner reference). Required by Epic sandbox."""

    description: Optional[str] = None
    """Human-readable description of the document."""

    context: Optional[Dict[str, Any]] = None
    """Context details for the document.

    Epic requires ``context.encounter`` for clinical note document types
    (e.g. LOINC 34108-1 Outpatient Note, 34117-2 History & Physical).
    Without it Epic returns::

        "diagnostics": "Valid encounter required",
        "expression": ["context/encounter"]

    Non-clinical document types (e.g. 34133-9 Summary of Episode) do NOT
    require an encounter.

    Example for clinical notes::

        {
            "encounter": [{"reference": "Encounter/<encounter_id>"}],
            "period": {"start": "2024-01-01T00:00:00Z", "end": "2024-01-01T01:00:00Z"}
        }
    """

    additional_fields: Optional[Dict[str, Any]] = None
    """Additional FHIR DocumentReference resource fields to merge into the payload."""


class FhirDocumentReferenceCreateOutput(BaseModel):
    """Output for creating a FHIR DocumentReference resource."""

    resource_id: str
    """The new DocumentReference resource ID."""

    resource: Optional[Dict[str, Any]] = None
    """The full created resource (only present when Prefer: return=representation)."""


# ---------------------------------------------------------------------------
# DocumentReference – Search
# ---------------------------------------------------------------------------

class FhirDocumentReferenceSearchInput(BaseModel):
    """Input for searching FHIR DocumentReference resources."""

    search_params: Dict[str, str]
    """Search parameters (e.g. {\"patient\": \"eXYZ123\"})."""


class FhirDocumentReferenceSearchOutput(BaseModel):
    """Output for searching FHIR DocumentReference resources."""

    resources: list[Dict[str, Any]]
    """The list of raw FHIR DocumentReference JSON objects found."""

    total: Optional[int] = None
    """Total number of results reported by the Bundle."""