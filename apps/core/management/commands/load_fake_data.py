from pathlib import Path

from django.core.management.base import BaseCommand
from django.core.management import call_command
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

        self.project_status = [
            status[0] for status in Project.Status.choices if status[0] != "none"
        ]

        self.task_status = [
            status[0] for status in Task.Status.choices if status[0] != "none"
        ]

        self.project_member_role = [
            role[0] for role in ProjectMember.Role.choices if role[0] != "none"
        ]

    def handle(self, *args, **kwargs):
        # Supprimer la base de données si elle existe
        db_path = Path("db.sqlite3")
        if db_path.exists():
            db_path.unlink()

        # Exécuter les migrations
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

        # Créer un utilisateur de test de type kk
        users_created.append(
            User.objects.create_user(
                username="kk",
                email="aliyaro104@gmail.com",
                password="projo#123",
                is_superuser=False,
                is_staff=False,
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
                status=self.fake.random_element(self.project_status),
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

            if (
                (user == project.author)
                or user.is_superuser
                or ProjectMember.objects.filter(project=project, user=user).exists()
            ):
                continue

            project_member = ProjectMember.objects.create(
                project=project,
                user=user,
                role=self.fake.random_element(self.project_member_role),
            )
            project_members_created.append(project_member)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Le membre du projet {project_member.project.title} a été créé avec succès!"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nTotal: {len(project_members_created)} membres de projets ont été créés."
            )
        )
        return project_members_created

    def create_fake_tasks(self, tasks_number, projects_created, users_created):
        authorized_users = []
        for user in users_created:
            # Vérifier si l'utilisateur est un superuser
            if user.is_superuser:
                authorized_users.append(user)
                continue

            # Vérifier si l'utilisateur est un modérateur ou propriétaire du projet
            for project in projects_created:
                if (
                    project.author == user
                    or ProjectMember.objects.filter(
                        project=project, user=user, role="moderator"
                    ).exists()
                ):
                    authorized_users.append(user)
                    break

        tasks_created = []
        for _ in range(tasks_number):
            task = Task.objects.create(
                title=self.fake.sentence(),
                description=self.fake.text(),
                author=self.fake.random_element(authorized_users),
                project=self.fake.random_element(projects_created),
                deadline=self.fake.date_between(start_date="-30d", end_date="+30d"),
                status=self.fake.random_element(self.task_status),
            )

            task.assigned_to.set(
                self.fake.random_elements(
                    elements=task.project.members.all(),
                    length=self.fake.random_int(min=1, max=5),
                )
            )
            tasks_created.append(task)
            self.stdout.write(
                self.style.SUCCESS(f"La tâche {task.title} a été créée avec succès!")
            )

        self.stdout.write(
            self.style.SUCCESS(f"\nTotal: {len(tasks_created)} tâches ont été créées.")
        )
        return tasks_created

    def create_fake_comments(self, comments_number, tasks_created, users_created):
        # Créer une liste des utilisateurs autorisés à commenter
        authorized_users = []
        # Ajouter l'admin
        admin = User.objects.get(username="admin")
        authorized_users.append(admin)

        for task in tasks_created:
            authorized_users.append(task.author)

            # Ajouter les modérateurs du projet
            moderators = ProjectMember.objects.filter(
                project=task.project, role="moderator"
            )
            for moderator in moderators:
                authorized_users.append(moderator.user)

            # Ajouter les utilisateurs assignés à la tâche
            authorized_users.extend(task.assigned_to.all())

        # Supprimer les doublons
        authorized_users = list(set(authorized_users))

        comments_created = []
        for _ in range(comments_number):
            comment = Comment.objects.create(
                task=self.fake.random_element(tasks_created),
                author=self.fake.random_element(authorized_users),
                content=self.fake.text(),
                created_at=self.fake.date_between(start_date="-30d", end_date="+30d"),
            )
            comments_created.append(comment)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Le commentaire {comment.content} a été créé avec succès!"
                )
            )

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
                title=self.fake.sentence(),
                content=self.fake.text(),
                is_read=self.fake.boolean(),
                created_at=self.fake.date_between(start_date="-30d", end_date="+30d"),
            )
            for _ in range(notifications_number)
        ]

        for notification in notifications_created:
            notification.recipients.set(
                self.fake.random_elements(
                    [user for user in users_created if user != notification.sender],
                    length=self.fake.random_int(min=1, max=len(users_created) - 1),
                )
            )
            notification.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"La notification {notification.title} a été créée avec succès!"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nTotal: {len(notifications_created)} notifications ont été créées."
            )
        )
        return notifications_created

    def create_admin_projects(self, users_created):
        admin = User.objects.get(username="admin")
        admin_projects = []

        # Créer 7 projets pour l'admin
        project_titles = [
            "Refonte du site web",
            "Application mobile",
            "Système de gestion des stocks",
            "Plateforme e-learning",
            "Système de facturation",
            "Gestion immobilière",
            "Controle qualité",
        ]
        for title in project_titles:
            project = Project.objects.create(
                title=title,
                description=self.fake.text(),
                author=admin,
                deadline=self.fake.date_between(start_date="+1d", end_date="+90d"),
                status=self.fake.random_element(self.project_status),
            )
            admin_projects.append(project)

            # Ajouter des membres au projet
            for _ in range(self.fake.random_int(min=3, max=9)):
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
                        role=self.fake.random_element(self.project_member_role),
                    )

            # Créer des tâches pour le projet
            for _ in range(self.fake.random_int(min=5, max=10)):
                task = Task.objects.create(
                    title=self.fake.sentence(),
                    description=self.fake.text(),
                    project=project,
                    author=admin,
                    status=self.fake.random_element(self.task_status),
                    deadline=self.fake.date_between(
                        start_date="+1d", end_date=project.deadline
                    ),
                )
                task.assigned_to.set(
                    self.fake.random_elements(
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
                        author=self.fake.random_element(
                            list(project.members.all()) + [admin]
                        ),
                        content=self.fake.text(),
                        created_at=self.fake.date_between(
                            start_date="-30d", end_date="now"
                        ),
                    )

        # Ajouter l'admin comme membre à 10 projets existants
        # existing_projects = Project.objects.exclude(author=admin)[:10]
        # for existing_project in existing_projects:
        #     if not ProjectMember.objects.filter(
        #         project=existing_project, user=admin
        #     ).exists():
        #         ProjectMember.objects.create(
        #             project=existing_project,
        #             user=admin,
        #             role=ProjectMember.Role.MODERATOR,
        #         )
        #         self.stdout.write(
        #             self.style.SUCCESS(
        #                 f"L'administrateur a été ajouté au projet {existing_project.title}"
        #             )
        #         )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nTotal: {len(admin_projects)} projets ont été créés pour l'administrateur."
            )
        )
        return admin_projects
