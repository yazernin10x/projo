from django.core.management.base import BaseCommand

from faker import Faker
from apps.accounts.models import User
from apps.notifications.models import Notification
from apps.projects.models import Project, ProjectMember
from apps.tasks.models import Task
from apps.comments.models import Comment


class Command(BaseCommand):
    help = "Load data into the database"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = Faker("fr_FR")

    def handle(self, *args, **kwargs):
        from pathlib import Path

        # Supprimer la base de données si elle existe
        db_path = Path("db.sqlite3")
        if db_path.exists():
            db_path.unlink()

        # Exécuter les migrations
        from django.core.management import call_command

        self.stdout.write("Exécution des migrations...")
        call_command("makemigrations")
        call_command("migrate")

        users_created = self.create_fake_users(30)
        projects_created = self.create_fake_projects(10, users_created)
        self.create_fake_project_members(50, projects_created, users_created)
        tasks_created = self.create_fake_tasks(70, projects_created, users_created)
        self.create_fake_comments(100, tasks_created, users_created)
        self.create_fake_notifications(100, users_created)
        self.create_admin_projects(users_created)

    def create_fake_users(self, users_number):
        users_created = []
        with open("fake_users.txt", "w") as f:
            for _ in range(users_number):
                username = self.fake.user_name()
                password = self.fake.password()

                # Écrire les informations dans le fichier
                f.write(f"Username: {username}, Password: {password}\n")

                # Créer l'utilisateur
                user = User.objects.create_user(
                    username=username,
                    email=self.fake.email(),
                    first_name=self.fake.first_name(),
                    last_name=self.fake.last_name(),
                    phone_number=self.fake.phone_number(),
                    password=password,
                )
                users_created.append(user)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"L'utilisateur {username} a été créé avec succès!"
                    )
                )

        # Créer le superuser admin
        admin = User.objects.create_superuser(
            username="admin", email="yazernin10x@gmail.com", password="projo#123"
        )
        users_created.append(admin)
        self.stdout.write(
            self.style.SUCCESS(f"Le superuser {admin.username} a été créé avec succès!")
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nTotal: {len(users_created)} utilisateurs ont été créés."
            )
        )
        return users_created

    def create_fake_projects(self, projects_number, users_created):
        projects_created = [
            Project.objects.create(
                title=self.fake.sentence(),
                description=self.fake.text(),
                author=self.fake.random_element(users_created),
                deadline=self.fake.date_between(start_date="-30d", end_date="+30d"),
            )
            for _ in range(projects_number)
        ]

        [
            self.stdout.write(
                self.style.SUCCESS(f"Le projet {project.title} a été créé avec succès!")
            )
            for project in projects_created
        ]

        self.stdout.write(
            self.style.SUCCESS(
                f"\nTotal: {len(projects_created)} projets ont été créés."
            )
        )
        return projects_created

    def create_fake_project_members(
        self, project_members_number, projects_created, users_created
    ):
        project_members_created = []
        for _ in range(project_members_number):
            project = self.fake.random_element(projects_created)
            user = self.fake.random_element(users_created)

            if not ProjectMember.objects.filter(project=project, user=user).exists():
                role_choices = [
                    role[0] for role in ProjectMember.Role.choices if role[0] != "none"
                ]
                project_member = ProjectMember.objects.create(
                    project=project,
                    user=user,
                    role=self.fake.random_element(role_choices),
                )
                project_members_created.append(project_member)

        [
            self.stdout.write(
                self.style.SUCCESS(
                    f"Le membre du projet {project_member.project.title} a été créé avec succès!"
                )
            )
            for project_member in project_members_created
        ]

        self.stdout.write(
            self.style.SUCCESS(
                f"\nTotal: {len(project_members_created)} membres de projets ont été créés."
            )
        )
        return project_members_created

    def create_fake_tasks(self, tasks_number, projects_created, users_created):
        status_choices = [
            status[0] for status in Task.Status.choices if status[0] != "none"
        ]
        tasks_created = [
            Task.objects.create(
                title=self.fake.sentence(),
                description=self.fake.text(),
                author=self.fake.random_element(users_created),
                project=self.fake.random_element(projects_created),
                deadline=self.fake.date_between(start_date="-30d", end_date="+30d"),
                status=self.fake.random_element(status_choices),
            )
            for _ in range(tasks_number)
        ]

        [
            task.assigned_to.add(
                *self.fake.random_elements(
                    elements=users_created, length=self.fake.random_int(min=1, max=5)
                )
            )
            for task in tasks_created
        ]

        [
            self.stdout.write(
                self.style.SUCCESS(f"La tâche {task.title} a été créée avec succès!")
            )
            for task in tasks_created
        ]

        self.stdout.write(
            self.style.SUCCESS(f"\nTotal: {len(tasks_created)} tâches ont été créées.")
        )
        return tasks_created

    def create_fake_comments(self, comments_number, tasks_created, users_created):
        comments_created = [
            Comment.objects.create(
                task=self.fake.random_element(tasks_created),
                author=self.fake.random_element(users_created),
                content=self.fake.text(),
                created_at=self.fake.date_between(start_date="-30d", end_date="+30d"),
            )
            for _ in range(comments_number)
        ]

        [
            self.stdout.write(
                self.style.SUCCESS(
                    f"Le commentaire {comment.content} a été créé avec succès!"
                )
            )
            for comment in comments_created
        ]

        self.stdout.write(
            self.style.SUCCESS(
                f"\nTotal: {len(comments_created)} commentaires ont été créés."
            )
        )
        return comments_created

    def create_fake_notifications(self, notifications_number, users_created):
        notifications_created = [
            Notification.objects.create(
                sender=self.fake.random_element(users_created),
                content=self.fake.text(),
                is_read=self.fake.boolean(),
                created_at=self.fake.date_between(start_date="-30d", end_date="+30d"),
            )
            for _ in range(notifications_number)
        ]

        [
            notification.recipients.add(
                *self.fake.random_elements(
                    [user for user in users_created if user != notification.sender],
                    length=self.fake.random_int(min=1, max=len(users_created) - 1),
                )
            )
            for notification in notifications_created
        ]

        [
            self.stdout.write(
                self.style.SUCCESS(
                    f"La notification {notification.content} a été créée avec succès!"
                )
            )
            for notification in notifications_created
        ]

        self.stdout.write(
            self.style.SUCCESS(
                f"\nTotal: {len(notifications_created)} notifications ont été créées."
            )
        )
        return notifications_created

    def create_admin_projects(self, users_created):
        admin = User.objects.get(username="admin")
        admin_projects = []

        # Créer 5 projets pour l'admin
        project_titles = [
            "Refonte du site web",
            "Application mobile",
            "Système de gestion des stocks",
            "Plateforme e-learning",
            "Système de facturation",
        ]

        for title in project_titles:
            project = Project.objects.create(
                title=title,
                description=self.fake.text(),
                author=admin,
                deadline=self.fake.date_between(start_date="+1d", end_date="+90d"),
            )
            admin_projects.append(project)

            # Ajouter des membres au projet
            role_choices = [
                role[0] for role in ProjectMember.Role.choices if role[0] != "none"
            ]
            for _ in range(self.fake.random_int(min=3, max=7)):
                user = self.fake.random_element(users_created)
                if (
                    user != admin
                    and not ProjectMember.objects.filter(
                        project=project, user=user
                    ).exists()
                ):
                    ProjectMember.objects.create(
                        project=project,
                        user=user,
                        role=self.fake.random_element(role_choices),
                    )
            # Ajouter l'admin comme membre à 10 projets existants
            existing_projects = Project.objects.exclude(id=project.id).order_by("?")[
                :10
            ]
            for existing_project in existing_projects:
                if not ProjectMember.objects.filter(
                    project=existing_project, user=admin
                ).exists():
                    ProjectMember.objects.create(
                        project=existing_project,
                        user=admin,
                        role=self.fake.random_element(role_choices),
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"L'administrateur a été ajouté au projet {existing_project.title}"
                        )
                    )
            # Créer des tâches pour le projet
            status_choices = [
                status[0] for status in Task.Status.choices if status[0] != "none"
            ]
            for _ in range(self.fake.random_int(min=5, max=10)):
                task = Task.objects.create(
                    title=self.fake.sentence(),
                    description=self.fake.text(),
                    project=project,
                    author=admin,
                    status=self.fake.random_element(status_choices),
                    deadline=self.fake.date_between(
                        start_date="+1d", end_date=project.deadline
                    ),
                )
                task.assigned_to.add(
                    *self.fake.random_elements(
                        elements=project.members.all(),
                        length=self.fake.random_int(
                            min=1, max=len(project.members.all())
                        ),
                    )
                )

                # Créer des commentaires pour la tâche
                for _ in range(self.fake.random_int(min=2, max=5)):
                    Comment.objects.create(
                        task=task,
                        author=self.fake.random_element(project.members.all()),
                        content=self.fake.text(),
                        created_at=self.fake.date_between(
                            start_date="-30d", end_date="now"
                        ),
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nTotal: {len(admin_projects)} projets ont été créés pour l'administrateur."
            )
        )
        return admin_projects
