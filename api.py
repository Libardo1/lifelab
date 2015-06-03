from flask import Flask, request, jsonify, make_response
from flask.ext import restful
from mongoengine import connect
from lifelab.models import Experiment, User, Variant
from lifelab.bandit import BayesianBandit
import json

app = Flask(__name__)
api = restful.Api(app)

connect('lifelab')


class ExperimentResource(restful.Resource):

    def post(self, version):
        request_data = request.get_json()
        variant_choice = request_data['variant_choice'] or "remember"
        experiment = Experiment(name=request_data['name'], variant_choice=variant_choice)
        experiment.save()
        data = request_data['data']
        variants = []
        for name, values in data.items():
            for value in values:
                variant = Variant(experiment=experiment, name=name,
                                data=value)
                variant.save()
                variants.append(variant.to_json())

        return make_response(jsonify(dict(variants=variants)), 200)

api.add_resource(ExperimentResource, '/<string:version>/experiments')


class VariantResource(restful.Resource):

    def get(self, version, variant_name):
        user_id = request.args.get('user_id')
        user = User.objects(id=user_id).modify(set__id=user_id, upsert=True, new=True)
        variant = Variant.objects(name=variant_name).first()
        variant_choice = variant.experiment.variant_choice
        if variant_choice == 'remember':
            variant = self.variant_choice_remember(variant_name, user)
        else:
            variant = self.variant_choice_forget(variant_name, user)
        variant_json = json.loads(variant.to_json())
        variant_json['id'] = variant_json['_id']['$oid']
        del variant_json['_id']
        return make_response(json.dumps(variant_json), 200)

    def variant_choice_remember(self, variant_name, user):
        variant = Variant.objects(name=variant_name).filter(users__all=[user]).first()
        if variant:
            return variant
        variant = self.variant_choice_forget(variant_name, user)
        if user in variant.experiment.excluded_users:
            # @TODO return original variant
            pass

        # @TODO decide to add user to the excluded
        variant.users.append(user)
        variant.save()
        return variant

    def variant_choice_forget(self, variant_name, user):
        variant = Variant.objects(name=variant_name).first()
        variants = Variant.objects(experiment=variant.experiment)
        arms = []
        for variant in variants:
            arms.append(dict(id=variant.id, successes=variant.successes, trials=variant.trials))
        bandit = BayesianBandit(arms)
        variant_id = bandit.choose_arm()
        return Variant.objects(id=variant_id).first()


api.add_resource(VariantResource, '/<string:version>/variants/<string:variant_name>')

class UpdateVariantResource(restful.Resource):

    def put(self, version, variant_id):
        variant = Variant.objects(id=variant_id).first()
        request_data = request.get_json()
        is_success = request_data['success']
        if is_success:
            variant['successes'] = variant['successes'] + 1
        variant['trials'] = variant['trials'] + 1
        variant.save()
        return make_response(variant.to_json(), 200)

api.add_resource(UpdateVariantResource, '/<string:version>/variants/<string:variant_id>')

if __name__ == '__main__':
    app.run(debug=True)
