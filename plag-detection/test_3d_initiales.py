import pygame
import sys

class Initiales:
    @staticmethod
    def show_initiales(s: str) -> None:
        pygame.init()

        # Set up display
        width, height = 400, 300
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("3D Initials")

        clock = pygame.time.Clock()

        # Colors
        white = (255, 255, 255)
        black = (0, 0, 0)
        shadow_color = (50, 50, 50)

        # Font
        font = pygame.font.Font(None, 150)

        def render_initials(initials):
            text_surface = font.render(initials, True, white)
            text_rect = text_surface.get_rect(center=(width // 2, height // 2))
            
            # Create a shadow surface
            shadow_surface = font.render(initials, True, shadow_color)
            shadow_rect = shadow_surface.get_rect(center=(text_rect.centerx + 5, text_rect.centery + 5))

            return text_surface, text_rect, shadow_surface, shadow_rect

        def main():
            initials = s.upper()

            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                screen.fill(black)

                text_surface, text_rect, shadow_surface, shadow_rect = render_initials(initials)

                # Draw the shadow first
                screen.blit(shadow_surface, shadow_rect)

                # Then draw the main text
                screen.blit(text_surface, text_rect)

                pygame.display.flip()
                clock.tick(30)

        if __name__ == "__main__":
            main()
