from landing.models import HeroContent
hero = HeroContent.objects.first()
if hero:
    hero.anim_text = "Maximize Your {img1} Brand's\nGrowth and {img2}{img3}{img4} Skyrocket Sales\nby Leveraging the Potential of\nCreator Marketing"
    hero.save()
