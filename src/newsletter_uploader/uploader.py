"""Newsletter uploader for Mailchimp campaigns."""
from pathlib import Path
from typing import Dict, Optional
from .audience import AudienceType, get_segment_opts
from .mailchimp_client import MailchimpClient


class NewsletterUploader:
    """Upload newsletters to Mailchimp as draft campaigns."""

    def __init__(self, client: MailchimpClient):
        """
        Initialize newsletter uploader.

        Args:
            client: Configured Mailchimp client
        """
        self.client = client

    def upload(
        self,
        html_file: Path,
        audience: AudienceType,
        subject: str,
        preview_text: str,
        title: Optional[str] = None,
    ) -> Dict:
        """
        Upload newsletter HTML as a draft Mailchimp campaign.

        Args:
            html_file: Path to HTML file to upload
            audience: Target audience (UK, US, or ALL)
            subject: Email subject line
            preview_text: Preview text shown in inbox
            title: Optional internal campaign title (defaults to filename)

        Returns:
            Dict with campaign_id and web_id

        Raises:
            FileNotFoundError: If HTML file doesn't exist
            Exception: If upload fails
        """
        # Read HTML file
        if not html_file.exists():
            raise FileNotFoundError(f"HTML file not found: {html_file}")

        html_content = html_file.read_text(encoding="utf-8")

        # Generate title from filename if not provided
        if title is None:
            title = html_file.stem

        # Get segment options for audience
        segment_opts = get_segment_opts(audience)

        # Create campaign
        campaign = self.client.create_campaign(
            subject=subject,
            preview_text=preview_text,
            title=title,
            segment_opts=segment_opts,
        )

        campaign_id = campaign["id"]
        web_id = campaign["web_id"]

        # Upload HTML content
        self.client.upload_content(campaign_id, html_content)

        return {
            "campaign_id": campaign_id,
            "web_id": web_id,
        }
