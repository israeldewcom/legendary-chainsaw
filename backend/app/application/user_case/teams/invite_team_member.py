from dataclasses import dataclass
import secrets
from app.domain.repositories.team import TeamRepository, TeamMemberRepository
from app.domain.repositories.user import UserRepository
from app.domain.entities.team import TeamMember
from app.application.interfaces.email_sender import EmailSender
from app.common.exceptions import NotFoundError, BusinessError
from app.config import settings
import structlog

logger = structlog.get_logger()


@dataclass
class InviteTeamMemberUseCase:
    team_repo: TeamRepository
    team_member_repo: TeamMemberRepository
    user_repo: UserRepository
    email_sender: EmailSender

    async def execute(self, team_id: int, inviter_id: int, email: str, role: str) -> None:
        team = await self.team_repo.get_by_id(team_id)
        if not team:
            raise NotFoundError("Team not found")

        # Check if inviter is owner or admin
        inviter_member = await self.team_member_repo.get_by_team_and_user(team_id, inviter_id)
        if not inviter_member or inviter_member.role not in ["owner", "admin"]:
            raise BusinessError("You don't have permission to invite members")

        # Check if user already exists
        user = await self.user_repo.get_by_email(email)
        if user:
            # Check if already member
            existing = await self.team_member_repo.get_by_team_and_user(team_id, user.id)
            if existing:
                raise BusinessError("User is already a member of this team")
            # Add directly
            member = TeamMember(team_id=team_id, user_id=user.id, role=role)
            await self.team_member_repo.save(member)
            # Send notification
            await self.email_sender.send_email(
                to=[email],
                subject=f"You've been added to team {team.name}",
                template_name="team_invite_existing.html",
                template_context={"team_name": team.name, "role": role}
            )
        else:
            # Invite non-user: create invitation token and send email
            token = secrets.token_urlsafe(32)
            # Store token in database (not implemented here)
            invite_link = f"{settings.FRONTEND_URL}/join-team?token={token}"
            await self.email_sender.send_email(
                to=[email],
                subject=f"Join team {team.name} on TaxFlow AI",
                template_name="team_invite_new.html",
                template_context={"team_name": team.name, "invite_link": invite_link}
            )

        logger.info("Team member invited", team_id=team_id, email=email, role=role)
