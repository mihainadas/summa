from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Processes a job with the given ID"

    def add_arguments(self, parser):
        # Adding an argument for process_job_id
        parser.add_argument(
            "process_job_id", type=int, help="The ID of the job to process"
        )

    def handle(self, *args, **options):
        process_job_id = options["process_job_id"]

        # Your code logic here
        try:
            # Replace this with the code you want to execute
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully processed job with ID {process_job_id}"
                )
            )
        except Exception as e:
            raise CommandError(
                f"Error processing job with ID {process_job_id}: {str(e)}"
            )
