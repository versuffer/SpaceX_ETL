"""Object URL count View

Revision ID: da7edabd3b76
Revises: 45a60290b914
Create Date: 2024-08-25 14:09:13.134338

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'da7edabd3b76'
down_revision: Union[str, None] = '45a60290b914'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Миграция создаёт View, подсчитывающее количество url для объектов launch, mission и rocket.

    Запрос:
    SELECT * FROM object_url_count;

    Пример вывода:
    "launches"	1811
    "missions"	0
    "rockets"	4
    """

    sql = """
    CREATE VIEW object_url_count AS
    SELECT object, url_COUNT FROM (
        SELECT 'launches' AS object, COUNT(*) AS url_COUNT FROM (
            SELECT article_link FROM launch_links WHERE launch_links IS NOT NULL
            UNION ALL
            SELECT unnest(flickr_images) AS urls FROM launch_links
            UNION ALL
            SELECT presskit FROM launch_links WHERE presskit IS NOT NULL
            UNION ALL
            SELECT reddit_campaign FROM launch_links WHERE reddit_campaign IS NOT NULL
            UNION ALL
            SELECT reddit_launch FROM launch_links WHERE reddit_launch IS NOT NULL
            UNION ALL
            SELECT reddit_media FROM launch_links WHERE reddit_media IS NOT NULL
            UNION ALL
            SELECT reddit_recovery FROM launch_links WHERE reddit_recovery IS NOT NULL
            UNION ALL
            SELECT video_link FROM launch_links WHERE video_link IS NOT NULL
            UNION ALL
            SELECT wikipedia FROM launch_links WHERE wikipedia IS NOT NULL
        )
        UNION ALL
        SELECT 'missions' AS object, COUNT(*) AS url_COUNT FROM (
            SELECT twitter FROM missions WHERE twitter IS NOT NULL
            UNION ALL
            SELECT website FROM missions WHERE website IS NOT NULL
            UNION ALL
            SELECT wikipedia FROM missions WHERE wikipedia IS NOT NULL
        )
        UNION ALL
        SELECT 'rockets' AS object, COUNT(*) AS url_COUNT FROM (
            SELECT wikipedia FROM rockets WHERE wikipedia IS NOT NULL
        )
    )
    """
    op.execute(sql)


def downgrade() -> None:
    op.execute('DROP VIEW object_url_count')
